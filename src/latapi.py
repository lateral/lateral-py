#!/usr/bin/env python

import requests, json, pandas as pd
from urlparse import urljoin
import collections

CsvDef = collections.namedtuple('CsvDef', 'file textfield metafields')


class LatRequest():
    """Basic requests to the Lateral API. Base class for higher level
    API wrapper classes"""

    def __init__(self, key, url="http://api.lateral.io", ignore=[406]):
        self.url_base = url
        self.key = key
        self.ignore = ignore

    def _url(self, endpoint):
        return urljoin(self.url_base, endpoint)

    def _hdr(self):
        return {'content-type': 'application/json',
                'subscription-key': self.key}

    def _request(self, method, endpoint, params=None, data={}):
        m = getattr(requests.api, method)
        resp = m(self._url(endpoint), headers=self._hdr(), params=params, data=data)
        C = resp.status_code
        if C / 100 == 2 or self.ignore.count(C):
            try:
                j = resp.json()
            except:
                print("response.raw: {}".format(resp.raw))
                raise ValueError("Response body is not valid json.")
            return resp     # success
        else:
            print resp.json()
            resp.raise_for_status()

    def _get(self, endpoint, params={}):
        return self._request('get', endpoint, params=params)

    def _post(self, endpoint, data={}):
        return self._request('post', endpoint, data=data)

    def _put(self, endpoint, data={}):
        return self._request('put', endpoint, data=data)

    def _delete(self, endpoint, data={}):
        return self._request('delete', endpoint, data=data)


class LatApi(LatRequest):
    """All Lateral API requests (but batch request"""

    ######################
    # Documents

    def get_documents(self, keywords=None):
        r = self._get('documents', {"keywords":keywords} if keywords else None)
        return r

    def post_document(self, text, meta={}):
        r = self._post('documents',
            json.dumps({"text": text, "meta": json.dumps(meta)}))
        return r

    def get_document(self, id):
        r = self._get('documents/{}'.format(id))
        return r

    def put_document(self, id, text, meta={}):
        r = self._put('documents/{}'.format(id),
            json.dumps({"text": text, "meta": json.dumps(meta)}))
        return r

    def delete_document(self, id):
        r = self._delete('documents/{}'.format(id))
        return r

    ######################
    # Users

    def get_users(self):
        r = self._get('users')
        return r

    def post_user(self):
        r = self._post('users')
        return r

    def get_user(self, id):
        r = self._get('users/{}'.format(id))
        return r

    def delete_user(self, id):
        r = self._delete('users/{}'.format(id))
        return r

    def get_user_recommendations(self, user_id, number, select_from=None):
        r = self._get('users/{}/recommendations'.format(user_id),
            params=json.dumps({"number": number, "select_from": select_from}))
        return r

    ######################
    # Preferences

    def get_preferences(self, user_id):
        r = self._get('users/{}/preferences'.format(user_id))
        return r

    def get_preference(self, user_id, document_id):
        r = self._get('users/{}/preferences/{}'.format(user_id, document_id))
        return r

    def post_preference(self, user_id, document_id):
        r = self._post('users/{}/preferences/{}'.format(user_id, document_id))
        return r

    def delete_preference(self, user_id, document_id):
        r = self._delete('users/{}/preferences/{}'.format(user_id, document_id))
        return r

    ######################
    # Clusters

    def get_cluster_models(self):
        r = self._get('cluster-models')
        return r

    def post_cluster_model(self, size):
        r = self._post('cluster-models', data = '{"number_clusters":%d}'%(size))
        return r

    def get_cluster_model(self, id):
        r = self._get('cluster-models/{}'.format(id))
        return r

    def delete_cluster_model(self, id):
        r = self._delete('cluster-models/{}'.format(id))
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


class LatApiLoader(LatApi):
    """Adds convenience functions to LatApi.
    Batch requests load csv files and save wordcloud images."""

    def create_meta(self, row, metafields):
        meta = dict([(dst, row[src]) for src, dst in metafields.iteritems()])
        return meta

    def create_batch_request_data(self, df, csvdef):
        rows = [df.loc[ind] for ind in df.index]
        opsdct = lambda row: {
                'method': 'POST',
                'url': '/documents',
                'params': {'text': json.dumps(row[csvdef.textfield]),
                           'meta': json.dumps(
                                self.create_meta(row, csvdef.metafields))},
                'headers': self.hdr()
            }
        ops = [opsdct(row) for row in rows]
        return ops

    def batch_post_request(self, ops):
        data = json.dumps({'ops': ops, 'sequential': 'true'})
        r = requests.request(
            'POST',
            self.url('batch'),
            headers=self.hdr(),
            data=data)
        return r

    def get_df(self, csvdef, chunksize):
        return pd.read_csv(csvdef.file, chunksize=chunksize, na_filter=False)

    def ingest(self, csvdef, batchsize=100, total=-1):
        success_cnt = 0
        for i, df in enumerate(self.get_df(csvdef, batchsize)):
            ops = self.create_batch_request_data(df, csvdef)
            r = self.batch_post_request(ops)
            results = dict(r.json())["results"]
            for j, res in enumerate(results):
                if res["status"] != 201 and res["status"] != 406:
                    print("Error for doc {doc} in batch {bat}:\n{res}".format(
                        doc=j, bat=i, res=json.dumps(
                            r.json(), sort_keys=True, indent=2)))
                    print("Document was: \n{}".format(json.dumps(ops)))
                else:
                    success_cnt += 1

            print("Chunk {}  status {}  {}".format(i, r.status_code, r.reason))
            if success_cnt % 500 == 0:
                gr = self.get_documents()
                print("{} documents total".format(gr.headers['total']))
            if total >= 0 and success_cnt >= total:
                break

    def save_wordclouds(self, cluster_model_id, file_prefix):
        clusters = json.loads(
            self.get_clusters_collection(cluster_model_id).content)
        for c in clusters:
            r = self.get_clusters_word_cloud(cluster_model_id, c)
            with open( "{}{:02d}.png".format(file_prefix, c), 'wb') as f:
                f.write(r.content)
