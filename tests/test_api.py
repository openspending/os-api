import zipfile
import json

import babbage_fiscal
import six

from flask.ext.testing import TestCase as FlaskTestCase

from os_api import config
from os_api.app import create_app


class TestAPI(FlaskTestCase):

    DATAPACKAGE_URL = "https://raw.githubusercontent.com/akariv/openspending-migrate/" \
                      "adam__test_datetime_dimension_change/examples/ukgov-finances-cra/datapackage.json"

    def create_app(self):
        app = create_app()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
        return app

    @classmethod
    def setUpClass(cls):
        super(TestAPI, cls).setUpClass()
        loader = babbage_fiscal.FDPLoader(engine=config.get_engine())
        loader.load_fdp_to_db(cls.DATAPACKAGE_URL, config.get_engine())

    def test_babbage_api_configured_success(self):
        res = self.client.get('/api/3/')
        assert res.status_code == 200
        assert res.json['status'] == 'ok'
        res = self.client.get('/api/3/cubes')
        assert res.status_code == 200
        assert 'ukgov-finances-cra' in [i['name'] for i in res.json['data']]

    def test_package_inspection_configured_success(self):
        res = self.client.get('/api/3/info/ukgov-finances-cra/package')
        assert res.status_code == 200
        assert res.json['name'] == 'ukgov-finances-cra'

    @staticmethod
    def compare_objects(o1,o2,prefix=''):
        allowed_missing_keys = {'cached', 'cache_key'}
        allowed_value_mismatch_keys = {'name', 'color', 'label', 'num_entries','errors', 'html_url','id'}
        err=[]
        k1 = set(o1.keys())
        k2 = set(o2.keys())
        if len(k1-k2-allowed_missing_keys)>0:
            err.append("Keys in 1st and not in 2nd: %s" % ", ".join(list(k1-k2)))
        if len(k2-k1-allowed_missing_keys)>0:
            err.append("Keys in 2st and not in 1st: %s" % ", ".join(list(k2-k1)))
        for k in k1:
            if k in k2:
                v1 = o1[k]
                v2 = o2[k]
                if type(v1) == type(v2):
                    if type(v1) in six.string_types or type(v1) is six.text_type or type(v1) in six.integer_types or type(v1) in (float, bool):
                        if v1 != v2:
                            if k not in allowed_value_mismatch_keys:
                                if type(v1) is float:
                                    if abs(v1 - v2)>1:
                                        err.append("Values for %s/%s are too different (%r,%r)" % (prefix,k,v1,v2))
                                else:
                                    err.append("Values for %s/%s are different (%r,%r)" % (prefix,k,v1,v2))
                    elif type(v1) is list:
                        if len(v1) != len(v2):
                            err.append("Lengths for %s/%s are different (%r,%r)" % (prefix,k,len(v1),len(v2)))
                        else:
                            errs_in_list = 0
                            for i in range(len(v1)):
                                if type(v1[i]) is dict and type(v2[i]) is dict:
                                    errs = TestAPI.compare_objects(v1[i],v2[i],prefix+'/%s[%d]' % (k,i))
                                else:
                                    errs = [] if v1[i] == v2[i] else ['Item mismatch: %r != %r' % (v1[i],v2[i])]
                                if len(errs)>0:
                                    err.extend(errs)
                                    errs_in_list+=1
                                    if errs_in_list == 3:
                                        err.append('more than 3 errors in list %s' % prefix)
                                        break
                    else:
                        err.extend(TestAPI.compare_objects(v1,v2,prefix+'/%s' % k))
                else:
                    err.append("Types for %s/%s are different (%r,%r)" % (prefix,k,v1,v2))
        return err

    def test_loader_and_backward_compatibility_api_success(self):
        responses = zipfile.ZipFile('tests/backward_responses.zip','r')
        for path in responses.namelist():
            canned_response = json.loads(responses.read(path).decode('utf8'))
            actual_response = self.client.get(path).json
            errors = TestAPI.compare_objects(canned_response,actual_response)
            assert len(errors) == 0




