#!/usr/bin/env python

import requests, json, pandas as pd
from urlparse import urljoin
import collections

CsvDef = collections.namedtuple('CsvDef', 'file textfield metafields')

class LatApi():
    def __init__(self, key, url="http://api.lateral.io"):
        self.url_base = url
        self.key = key

    def url(self, path_str):
        return urljoin(self.url_base, path_str)

    def hdr(self):
        return {'content-type': 'application/json',
                'subscription-key': self.key}

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

    ###########
    # Documents

    def post_document(self, text, meta={}):
        r = requests.request('POST',
            self.url('documents'),
            headers = self.hdr(),
            data = json.dumps({"text": text, "meta": meta}))
        return r

    def get_documents(self, keywords=None):
        r = requests.request('GET',
            self.url('documents'),
            headers = self.hdr(),
            params = {"keywords":keywords} if keywords else None)
        return r

    ###########
    # Users

    def post_user(self):
        r = requests.request('POST',
            self.url('cluster-models'),
            headers = self.hdr(),
            data = '{"number_clusters":%d}' % (size))
        return r

    def get_users(self):
        r = requests.request('GET',
            self.url('users'),
            headers = self.hdr())
        return r

    def get_user(self, id):
        r = requests.request('GET',
            self.url('users/{}'.format(id)),
            headers = self.hdr())
        return r

    def delete_user(self, id):
        r = requests.request('DELETE',
            self.url('users/{}'.format(id)),
            headers = self.hdr())
        return r

    ###########
    # Recommend

    def get_user_recommendations(self, user_id, number, select_from=None):
        r = requests.request('GET',
            self.url('users/{}/recommendations'.format(user_id)),
            headers = self.hdr(),
            params = json.dumps({"number": number, "select_from": select_from}))
        return r

    ###########
    # Users

    def post_preference(self, user_id, document_id):
        r = requests.request('POST',
            self.url('users/{}/preferences/{}'.format(
                user_id, document_id)),
            headers = self.hdr())
        return r

    def get_preferences_collection(self, user_id):
        r = requests.request('GET',
            self.url('users/{}/preferences'.format(user_id)),
            headers = self.hdr())
        return r

    def get_preferences(self, user_id, document_id):
        r = requests.request('GET',
            self.url('users/{}/preferences/{}'.format(
                user_id, document_id)),
            headers = self.hdr())
        return r

    def delete_preferences(self, user_id, document_id):
        r = requests.request('DELETE',
            self.url('users/{}/preferences/{}'.format(
                user_id, document_id)),
            headers = self.hdr())
        return r

    ###########
    # Clusters

    def post_cluster_model(self, size):
        r = requests.request('POST',
            self.url('cluster-models'),
            headers = self.hdr(),
            data = '{"number_clusters":%d}' % (size))
        return r

    def get_cluster_models(self):
        r = requests.request('GET',
            self.url('cluster-models'),
            headers = self.hdr())
        return r

    def get_cluster_model(self, id):
        r = requests.request('GET',
            self.url('cluster-models/{}'.format(id)),
            headers = self.hdr())
        return r

    def delete_cluster_model(self, id):
        r = requests.request('DELETE',
            self.url('cluster-models/{}'.format(id)),
            headers = self.hdr())
        return r

    def get_clusters_collection(self, cluster_model_id):
        r = requests.request('GET',
            self.url('cluster-models/{}/clusters'.format(cluster_model_id)),
            headers = self.hdr())
        return r

    def get_clusters_words_collection(self, cluster_model_id, cluster_id):
        r = requests.request('GET',
            self.url('cluster-models/{}/clusters/{}/words'.format(
                cluster_model_id, cluster_id)),
            headers = self.hdr())
        return r

    def get_clusters_word_cloud(self, cluster_model_id, cluster_id):
        r = requests.request('GET',
            self.url('cluster-models/{}/clusters/{}/word-cloud'.format(
                cluster_model_id, cluster_id)),
            headers = self.hdr())
        return r

    ###########
    # Generic

    def delete_all_data(self):
        r = requests.request('DELETE',
            self.url('delete-all-data'),
            headers = self.hdr())
        return r

