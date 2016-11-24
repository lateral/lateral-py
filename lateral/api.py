"""
Implements class :py:class:`lateral.api.Request` and subclass
:py:class:`lateral.api.API` that wrap the Lateral API.

NOTE we chose to return requests.Response objects rather than the decoded JSON
since the pagination information is only made available in the response
headers.
"""

import requests
import ujson
from urlparse import urljoin


class Request():
    """Basic requests to the Lateral API. Base class for higher level
    API wrapper classes."""

    def __init__(self, key, url="http://api-v4.lateral.io", ignore=[406]):
        """
        :param key: subscription key
        :param url: url of lateral instance
        :param ignore: list of integers representing status_codes that are not
        considered an error (default [406])
        """
        self.url_base = url
        self.key = key
        self.ignore = ignore
        self.counter = 0

    def _url(self, endpoint):
        return urljoin(self.url_base, endpoint)

    def _hdr(self):
        return {'content-type': 'application/json',
                'subscription-key': self.key}

    def _request(self, method, endpoint, params=None, data={}):
        self.counter += 1
        m = getattr(requests.api, method)
        resp = m(self._url(endpoint), headers=self._hdr(), params=params,
                 data=data)
        C = resp.status_code
        if C / 100 == 2 or self.ignore.count(C):
            return resp     # success
        else:
            resp.raise_for_status()

    def _get(self, endpoint, **params):
        return self._request('get', endpoint, params=params)

    def _post(self, endpoint, data={}):
        return self._request('post', endpoint, data=data)

    def _put(self, endpoint, data={}):
        return self._request('put', endpoint, data=data)

    def _delete(self, endpoint, data={}):
        return self._request('delete', endpoint, data=data)


def append_id(endpoint, _id):
    """
    append '_id' to endpoint if provided
    """
    if _id is not None:
        return '/'.join([endpoint.rstrip('/'), _id])
    return endpoint


class API(Request):
    """All Lateral API requests (but batch request)."""

    ######################
    # Documents

    def get_documents(self, **params):
        r = self._get('documents', **params)
        return r

    def post_document(self, text, meta={}, document_id=None):
        r = self._post(append_id('documents', document_id),
                       ujson.dumps({"text": text, "meta": ujson.dumps(meta)}))
        return r

    def get_document(self, document_id):
        r = self._get('documents/{}'.format(document_id))
        return r

    def put_document(self, document_id, text, meta={}):
        r = self._put('documents/{}'.format(document_id),
                      ujson.dumps({"text": text, "meta": ujson.dumps(meta)}))
        return r

    def delete_document(self, document_id):
        r = self._delete('documents/{}'.format(document_id))
        return r

    def get_documents_tags(self, document_id, **params):
        r = self._get('documents/{}/tags'.format(document_id), **params)
        return r

    def get_documents_preferences(self, document_id, **params):
        r = self._get('documents/{}/preferences'.format(document_id), **params)
        return r

    def get_documents_similar(self, document_id, **params):
        r = self._get('documents/{}/similar'.format(document_id), **params)
        return r

    def post_documents_similar_to_text(self, text, **params):
        params['text'] = text
        r = self._post('documents/similar-to-text', ujson.dumps(params))
        return r

    def post_documents_popular(self, **params):
        r = self._post('documents/popular', ujson.dumps(params))
        return r

    ######################
    # Tags

    def get_tags(self):
        r = self._get('tags')
        return r

    def post_tag(self, tag_id):
        r = self._post('tags/{}'.format(tag_id))
        return r

    def get_tag(self, tag_id):
        r = self._get('tags/{}'.format(tag_id))
        return r

    def delete_tag(self, tag_id):
        r = self._delete('tags/{}'.format(tag_id))
        return r

    ######################
    # Taggings

    def get_tags_documents(self, tag_id, **params):
        r = self._get('tags/{}/documents'.format(tag_id), **params)
        return r

    def post_documents_tagging(self, document_id, tag_id):
        r = self._post('documents/{}/tags/{}'.format(document_id, tag_id))
        return r

    def delete_documents_tagging(self, document_id, tag_id):
        r = self._delete('documents/{}/tags/{}'.format(document_id, tag_id))
        return r

    ######################
    # Users

    def get_users(self, **params):
        r = self._get('users', **params)
        return r

    def post_user(self, user_id=None):
        r = self._post(append_id('users', user_id))
        return r

    def get_user(self, id):
        r = self._get('users/{}'.format(id))
        return r

    def delete_user(self, id):
        r = self._delete('users/{}'.format(id))
        return r

    def get_user_recommendations(self, user_id, **params):
        r = self._get('users/{}/recommendations'.format(user_id),
                      params=ujson.dumps(params))
        return r

    ######################
    # Preferences

    def get_users_preferences(self, user_id):
        r = self._get('users/{}/preferences'.format(user_id))
        return r

    def get_users_preference(self, user_id, document_id):
        r = self._get('users/{}/preferences/{}'.format(user_id, document_id))
        return r

    def post_users_preference(self, user_id, document_id):
        r = self._post('users/{}/preferences/{}'.format(user_id, document_id))
        return r

    def delete_users_preference(self, user_id, document_id):
        r = self._delete('users/{}/preferences/{}'.format(user_id, document_id))
        return r

    ######################
    # Clusters

    def get_cluster_models(self, **params):
        r = self._get('cluster-models', **params)
        return r

    def post_cluster_model(self, size):
        r = self._post('cluster-models', data='{"number_clusters":%d}' % (size))
        return r

    def get_cluster_model(self, cluster_model_id):
        r = self._get('cluster-models/{}'.format(cluster_model_id))
        return r

    def delete_cluster_model(self, cluster_model_id):
        r = self._delete('cluster-models/{}'.format(cluster_model_id))
        return r

    def get_clusters(self, cluster_model_id):
        r = self._get('cluster-models/{}/clusters'.format(cluster_model_id))
        return r

    def get_clusters_documents(self, cluster_model_id, cluster_id):
        r = self._get('cluster-models/{}/clusters/{}/documents'.format(
            cluster_model_id, cluster_id))
        return r

    def get_clusters_words(self, cluster_model_id, cluster_id):
        r = self._get('cluster-models/{}/clusters/{}/words'.format(
            cluster_model_id, cluster_id))
        return r

    def get_clusters_word_cloud(self, cluster_model_id, cluster_id):
        r = self._get('cluster-models/{}/clusters/{}/word-cloud'.format(
                cluster_model_id, cluster_id))
        return r

    ######################
    # Generic

    def delete_all_data(self):
        r = self._delete('delete-all-data')
        return r
