
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
