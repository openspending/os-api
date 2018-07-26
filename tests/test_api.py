import zipfile
import json
import six
import pytest


class TestAPI(object):
    def test_babbage_api_configured_success(self, client):
        res = client.get('/api/3/')
        assert res.status_code == 200
        assert res.json['status'] == 'ok'
        res = client.get('/api/3/cubes/')
        assert res.status_code == 200
        assert '__testing:ukgov-finances-cra' \
            in [i['name'] for i in res.json['data']]

    def test_package_inspection_configured_success(self, client):
        res = client.get('/api/3/info/__testing:ukgov-finances-cra/package')
        assert res.status_code == 200
        assert res.json['name'] == 'ukgov-finances-cra'

    def test_package_inspection_configured_notfound(self, client):
        res = client.get('/api/3/info/__testing:no-package-here/package')
        assert res.status_code == 404

    @pytest.mark.skip
    def test_loader_and_backward_compatibility_api_success(self, client):
        responses = zipfile.ZipFile('tests/backward_responses.zip', 'r')
        for path in responses.namelist():
            canned_response = json.loads(responses.read(path).decode('utf8'))
            path = path.replace('=ukgov-finances-cra',
                                '=__testing:ukgov_finances_cra')
            actual_response = client.get(path).json
            errors = compare_objects(canned_response, actual_response)
            if len(errors) > 0:
                print('URL:\n', path)
                print('Expected:\n', canned_response)
                print('Actual:\n', actual_response)
            assert len(errors) == 0

    def test_loader_and_backward_compatibility_api_errors(self, client):
        responses = \
            zipfile.ZipFile('tests/backward_mismatch_responses.zip', 'r')
        for path in responses.namelist():
            canned_response = json.loads(responses.read(path).decode('utf8'))
            actual_response = client.get(path).json
            errors = compare_objects(canned_response, actual_response)
            assert len(errors) > 0


def compare_objects(o1, o2, prefix=''):
    allowed_missing_keys = {'cached', 'cache_key'}
    allowed_value_mismatch_keys = {'name', 'color', 'label', 'num_entries',
                                   'errors', 'html_url', 'id'}
    err = []
    k1 = set(o1.keys())
    k2 = set(o2.keys())
    if len(k1-k2-allowed_missing_keys) > 0:
        err.append("Keys in 1st and not in 2nd: %s" % ", ".join(list(k1-k2)))
    if len(k2-k1-allowed_missing_keys) > 0:
        err.append("Keys in 2st and not in 1st: %s" % ", ".join(list(k2-k1)))
    for k in k1:
        if k in k2:
            v1 = o1[k]
            v2 = o2[k]
            if type(v1) == type(v2):
                if type(v1) in six.string_types \
                   or type(v1) is six.text_type \
                   or type(v1) in six.integer_types \
                   or type(v1) in (float, bool):
                    if v1 != v2:
                        if k not in allowed_value_mismatch_keys:
                            if type(v1) is float:
                                if abs(v1 - v2) > 1:
                                    msg = "Values for %s/%s are too " \
                                          "different (%r,%r)"
                                    err.append(msg % (prefix, k, v1, v2))
                            else:
                                msg = "Values for %s/%s are different (%r,%r)"
                                err.append(msg % (prefix, k, v1, v2))
                elif type(v1) is list:
                    if len(v1) != len(v2):
                        msg = "Lengths for %s/%s are different (%r,%r)"
                        err.append(msg % (prefix, k, len(v1), len(v2)))
                    else:
                        errs_in_list = 0
                        for i in range(len(v1)):
                            if type(v1[i]) is dict and type(v2[i]) is dict:
                                errs = TestAPI.compare_objects(
                                    v1[i],
                                    v2[i],
                                    prefix + '/%s[%d]' % (k, i))
                            else:
                                errs = [] if v1[i] == v2[i] \
                                          else ['Item mismatch: %r != %r' % (v1[i], v2[i])]  # noqa
                            if len(errs) > 0:
                                err.extend(errs)
                                errs_in_list += 1
                                if errs_in_list == 3:
                                    msg = 'more than 3 errors in list %s'
                                    err.append(msg % prefix)
                                    break
                else:
                    err.extend(TestAPI.compare_objects(
                        v1, v2, prefix+'/%s' % k))
            else:
                msg = "Types for %s/%s are different (%r,%r)"
                err.append(msg % (prefix, k, v1, v2))
    return err
