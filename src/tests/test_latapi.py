import requests, responses, unittest, json
import latapi

class LatApiTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://test.io"
        self.api = latapi.LatApi("009b64acf288f20816ecfbbd20000000",
            url=self.url, ignore=[666])
        self.jsonX = {"id": 1}
        self.X = json.dumps(self.jsonX)

    def tearDown(self):
        pass

    @responses.activate
    def test_request(self):
        responses.add(responses.GET, 'http://test.io/2xx', status=299, body=self.X)
        responses.add(responses.GET, 'http://test.io/666', status=666, body=self.X)
        try:
            self.api._request('get', 'http://test.io/2xx')
            self.api._request('get', 'http://test.io/666')
        except:
            self.fail("Function _request throws exception on legal input.")

        responses.add(responses.GET, 'http://test.io/4xx', status=499, body=self.X)
        with self.assertRaises(requests.exceptions.HTTPError):
            self.api._request('get', 'http://test.io/4xx')

        responses.add(responses.GET, 'http://test.io/200', status=200, body='"x": 3}')
        with self.assertRaises(ValueError):
            self.api._request('get', 'http://test.io/200')

    ######################
    # Documents

    @responses.activate
    def test_get_documents(self):
        responses.add(responses.GET, 'http://test.io/documents', status=200, body=self.X)
        r = self.api.get_documents()
        assert r.json() == self.jsonX

        responses.add(responses.GET, 'http://test.io/documents?keywords=lorem', status=200, body=self.X)
        r = self.api.get_documents('lorem')
        assert r.json() == self.jsonX

    @responses.activate
    def test_post_document(self):
        responses.add(responses.POST, 'http://test.io/documents', status=201, body=self.X)
        r = self.api.post_document('Fat black cat', {"title": "Lorem ipsum"})
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_document(self):
        responses.add(responses.GET, 'http://test.io/documents/docx', status=201, body=self.X)
        r = self.api.get_document('docx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_put_document(self):
        responses.add(responses.PUT, 'http://test.io/documents/docx', status=200, body=self.X)
        r = self.api.put_document('docx', 'Fat black cat', {"title": "Lorem ipsum"})
        assert r.json() == self.jsonX

    @responses.activate
    def test_delete_document(self):
        responses.add(responses.DELETE, 'http://test.io/documents/docx', status=201, body=self.X)
        r = self.api.delete_document('docx')
        assert r.json() == self.jsonX

    ######################
    # Users

    @responses.activate
    def test_post_user(self):
        responses.add(responses.POST, 'http://test.io/users', status=201, body=self.X)
        r = self.api.post_user()
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_users(self):
        responses.add(responses.GET, 'http://test.io/users', status=200, body=self.X)
        r = self.api.get_users()
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_user(self):
        responses.add(responses.GET, 'http://test.io/users/userx', status=201, body=self.X)
        r = self.api.get_user('userx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_delete_user(self):
        responses.add(responses.DELETE, 'http://test.io/users/userx', status=201, body=self.X)
        r = self.api.delete_user('userx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_user_recommendations(self):
        responses.add(responses.GET, 'http://test.io/users/user_all/recommendations', status=201, body=self.X)
        r = self.api.get_user_recommendations('user_all', 10)
        assert r.json() == self.jsonX

        responses.add(responses.GET, 'http://test.io/users/user_sel/recommendations', status=201, body=self.X)
        r = self.api.get_user_recommendations('user_sel', 10, [1, 2, 3, 4])
        assert r.json() == self.jsonX

    ######################
    # Preferences

    @responses.activate
    def test_get_preferences(self):
        responses.add(responses.GET, 'http://test.io/users/userx/preferences', status=200, body=self.X)
        r = self.api.get_preferences('userx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_preference(self):
        responses.add(responses.GET, 'http://test.io/users/userx/preferences/docx', status=201, body=self.X)
        r = self.api.get_preference('userx', 'docx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_post_preference(self):
        responses.add(responses.POST, 'http://test.io/users/userx/preferences/docx', status=201, body=self.X)
        r = self.api.post_preference('userx', 'docx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_delete_preference(self):
        responses.add(responses.DELETE, 'http://test.io/users/userx/preferences/docx', status=200, body=self.X)
        r = self.api.delete_preference('userx', 'docx')
        assert r.json() == self.jsonX

    ######################
    # Clusters

    @responses.activate
    def test_get_cluster_models(self):
        responses.add(responses.GET, 'http://test.io/cluster-models', status=200, body=self.X)
        r = self.api.get_cluster_models()
        assert r.json() == self.jsonX

    @responses.activate
    def test_post_cluster_model(self):
        responses.add(responses.POST, 'http://test.io/cluster-models', status=201, body=self.X)
        r = self.api.post_cluster_model(10)
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_cluster_model(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx', status=201, body=self.X)
        r = self.api.get_cluster_model('modelx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_delete_cluster_model(self):
        responses.add(responses.DELETE, 'http://test.io/cluster-models/modelx', status=201, body=self.X)
        r = self.api.delete_cluster_model('modelx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_clusters(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters', status=200, body=self.X)
        r = self.api.get_clusters('modelx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_clusters_documents(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters/clustx/documents', status=200, body=self.X)
        r = self.api.get_clusters_documents('modelx', 'clustx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_clusters_words(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters/clustx/words', status=200, body=self.X)
        r = self.api.get_clusters_words('modelx', 'clustx')
        assert r.json() == self.jsonX

    @responses.activate
    def test_get_clusters_word_cloud(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters/clustx/words', status=200, body=self.X)
        r = self.api.get_clusters_words('modelx', 'clustx')
        assert r.json() == self.jsonX

