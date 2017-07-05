import zipfile

import six
import json
import requests
import time


def get(path):
    print('<<< %s' % path)
    return requests.get('https://staging.openspending.org' + path + '&_cb=%s' % time.time()).json()


def compare_objects(o1,o2,prefix=''):
    allowed_missing_keys = {'cached', 'cache_key', 'color', 'gov_department', 'description'}
    allowed_value_mismatch_keys = {'name', 'label', 'num_entries','errors', 'html_url','id', 'taxonomy'}
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
                                errs = compare_objects(v1[i],v2[i],prefix+'/%s[%d]' % (k,i))
                            else:
                                errs = [] if v1[i] == v2[i] else ['Item mismatch: %r != %r' % (v1[i],v2[i])]
                            if len(errs)>0:
                                err.extend(errs)
                                errs_in_list+=1
                                if errs_in_list == 3:
                                    err.append('more than 3 errors in list %s' % prefix)
                                    break
                else:
                    err.extend(compare_objects(v1,v2,prefix+'/%s' % k))
            else:
                err.append("Types for %s/%s are different (%r,%r)" % (prefix,k,v1,v2))
    return err

okayed = set(open('tested-ok.txt').read().split('\n'))
ok = open('tested-ok.txt', 'a')

def test_loader_and_backward_compatibility_api_success():
    count = 0
    responses = zipfile.ZipFile('backward_responses.zip','r')
    for path in responses.namelist():
        count += 1
        if path not in okayed:
            canned_response = json.loads(responses.read(path).decode('utf8'))
            # path = path.replace('=ukgov-finances-cra','=__testing:ukgov-finances-cra')
            actual_response = get(path)
            errors = compare_objects(canned_response, actual_response)
            if len(errors)>0:
                print('ERRd URL:', path)
                print('%d Errors, e.g.:' % len(errors), errors[0])
                # print('Expected:\n',canned_response)
                # print('Actual:\n',actual_response)
            else:
                print('OK URL:', path)
                ok.write(path + '\n')
                ok.flush()
            # assert len(errors) == 0
    return count


def test_loader_and_backward_compatibility_api_errors():
    count = 0
    responses = zipfile.ZipFile('backward_mismatch_responses.zip','r')
    for path in responses.namelist():
        count += 1
        if path not in okayed:
            canned_response = json.loads(responses.read(path).decode('utf8'))
            actual_response = get(path)
            errors = compare_objects(canned_response, actual_response)
            if len(errors) == 0:
                print('NOT ERRd URL:', path)
                # print('Expected:\n',canned_response)
                # print('Actual:\n',actual_response)
            else:
                print('OK URL:', path)
                ok.write(path + '\n')
                ok.flush()
    return count


if __name__ == '__main__':
    print('GOOD URLS:', test_loader_and_backward_compatibility_api_success())
    print('BAD URLS:', test_loader_and_backward_compatibility_api_errors())
    ok.close()