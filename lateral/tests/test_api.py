import requests, responses, unittest, json
import lateral.api

class ApiTest(unittest.TestCase):

    def setUp(self):
        self.url = "http://test.io"
        self.api = lateral.api.Api("009b64acf288f20816ecfbbd20000000",
            url=self.url, ignore=[666])
        self.jsonX = {"id": 1}
        self.X = json.dumps(self.jsonX)

    def tearDown(self):
        pass

    @responses.activate
    def test_request(self):
        responses.add(responses.GET, 'http://test.io/2xx', status=299, body=self.X)
        responses.add(responses.GET, 'http://test.io/666', status=666, body="")
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

        r = self.api.get_documents('lorem', page=3, per_page=5) # keywords + pagination
        assert responses.calls[1].request.url.find("keywords=lorem") > 0

        r = self.api.get_documents(page=3, per_page=5) # pagination alone
        assert responses.calls[2].request.url.find("page=3") > 0
        assert responses.calls[2].request.url.find("per_page=5") > 0

    @responses.activate
    def test_post_document(self):
        responses.add(responses.POST, 'http://test.io/documents', status=201, body=self.X)
        r = self.api.post_document('Fat black cat', {"title": "Lorem ipsum"})

    @responses.activate
    def test_get_document(self):
        responses.add(responses.GET, 'http://test.io/documents/docx', status=201, body=self.X)
        r = self.api.get_document('docx')

    @responses.activate
    def test_put_document(self):
        responses.add(responses.PUT, 'http://test.io/documents/docx', status=200, body=self.X)
        r = self.api.put_document('docx', 'Fat black cat', {"title": "Lorem ipsum"})

    @responses.activate
    def test_delete_document(self):
        responses.add(responses.DELETE, 'http://test.io/documents/docx', status=201, body=self.X)
        r = self.api.delete_document('docx')

    ######################
    # Users

    @responses.activate
    def test_post_user(self):
        responses.add(responses.POST, 'http://test.io/users', status=201, body=self.X)
        r = self.api.post_user()

    @responses.activate
    def test_get_users(self):
        responses.add(responses.GET, 'http://test.io/users', status=200, body=self.X)
        r = self.api.get_users()

        r = self.api.get_users(page=3, per_page=5)
        assert responses.calls[1].request.url.find("page=3") > 0
        assert responses.calls[1].request.url.find("per_page=5") > 0

    @responses.activate
    def test_get_user(self):
        responses.add(responses.GET, 'http://test.io/users/userx', status=201, body=self.X)
        r = self.api.get_user('userx')

    @responses.activate
    def test_delete_user(self):
        responses.add(responses.DELETE, 'http://test.io/users/userx', status=201, body=self.X)
        r = self.api.delete_user('userx')

    @responses.activate
    def test_get_user_recommendations(self):
        responses.add(responses.GET, 'http://test.io/users/user_all/recommendations', status=201, body=self.X)
        r = self.api.get_user_recommendations('user_all', 10)

        responses.add(responses.GET, 'http://test.io/users/user_sel/recommendations', status=201, body=self.X)
        r = self.api.get_user_recommendations('user_sel', 10, [1, 2, 3, 4])

    ######################
    # Preferences

    @responses.activate
    def test_get_preferences(self):
        responses.add(responses.GET, 'http://test.io/users/userx/preferences', status=200, body=self.X)
        r = self.api.get_preferences('userx')

    @responses.activate
    def test_get_preference(self):
        responses.add(responses.GET, 'http://test.io/users/userx/preferences/docx', status=201, body=self.X)
        r = self.api.get_preference('userx', 'docx')

    @responses.activate
    def test_post_preference(self):
        responses.add(responses.POST, 'http://test.io/users/userx/preferences/docx', status=201, body=self.X)
        r = self.api.post_preference('userx', 'docx')

    @responses.activate
    def test_delete_preference(self):
        responses.add(responses.DELETE, 'http://test.io/users/userx/preferences/docx', status=200, body=self.X)
        r = self.api.delete_preference('userx', 'docx')

    ######################
    # Clusters

    @responses.activate
    def test_get_cluster_models(self):
        responses.add(responses.GET, 'http://test.io/cluster-models', status=200, body=self.X)
        r = self.api.get_cluster_models()

        r = self.api.get_cluster_models(page=3, per_page=5)
        assert responses.calls[1].request.url.find("page=3") > 0
        assert responses.calls[1].request.url.find("per_page=5") > 0


    @responses.activate
    def test_post_cluster_model(self):
        responses.add(responses.POST, 'http://test.io/cluster-models', status=201, body=self.X)
        r = self.api.post_cluster_model(10)

    @responses.activate
    def test_get_cluster_model(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx', status=201, body=self.X)
        r = self.api.get_cluster_model('modelx')

    @responses.activate
    def test_delete_cluster_model(self):
        responses.add(responses.DELETE, 'http://test.io/cluster-models/modelx', status=201, body=self.X)
        r = self.api.delete_cluster_model('modelx')

    @responses.activate
    def test_get_clusters(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters', status=200, body=self.X)
        r = self.api.get_clusters('modelx')

    @responses.activate
    def test_get_clusters_documents(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters/clustx/documents', status=200, body=self.X)
        r = self.api.get_clusters_documents('modelx', 'clustx')

    @responses.activate
    def test_get_clusters_words(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters/clustx/words', status=200, body=self.X)
        r = self.api.get_clusters_words('modelx', 'clustx')

    @responses.activate
    def test_get_clusters_word_cloud(self):
        responses.add(responses.GET, 'http://test.io/cluster-models/modelx/clusters/clustx/words', status=200, body=self.X)
        r = self.api.get_clusters_words('modelx', 'clustx')

