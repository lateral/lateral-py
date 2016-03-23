"""
Implements subclass of :py:class:`lateral.api.Api` to send data from a csv to the Lateral Api.
"""
import requests, json, pandas as pd, collections
import lateral.api

CsvDef = collections.namedtuple('CsvDef', 'file textfield metafields')

class ApiLoader(lateral.api.Api):
    """Adds convenience functions to :py:class:`lateral.Api`."""

    def create_meta(self, row, metafields):
        meta = dict([(dst, row[src]) for src, dst in metafields.iteritems()])
        return meta

    def create_batch_request_data(self, df, csvdef):
        rows = [df.loc[ind] for ind in df.index]
        opsdct = lambda row: {
                'method': 'POST',
                'url': '/documents',
                'params': {'text': row[csvdef.textfield],
                           'meta': json.dumps(
                                self.create_meta(row, csvdef.metafields))},
                'headers': self._hdr()
            }
        ops = [opsdct(row) for row in rows]
        return ops

    def batch_post_request(self, ops):
        data = json.dumps({'ops': ops, 'sequential': 'true'})
        r = requests.request(
            'POST',
            self._url('batch'),
            headers=self._hdr(),
            data=data)
        return r

    def get_df(self, csvdef, chunksize):
        return pd.read_csv(csvdef.file, chunksize=chunksize, na_filter=False)

    def ingest(self, csvdef, batchsize=100, total=-1):
        """Do batch requests to load csv file. The pandas csv reader is used.
        Be sure your csv is appropriate.
        :param csvdef: namedtuple with filename, name of column with text content,
        dictionary that maps column names in csv to meta field names
        :param batchsize: size of batches (note that 100 is maximum)
        :param total: number of entries to take from csv
        """
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
        """Download wordcloud images.
        :param cluster_model_id: cluster model id
        :param file_prefix: images are stored to files `file_prefixN.png` for cluster N
        """
        clusters = json.loads(
            self.get_clusters_collection(cluster_model_id).content)
        for c in clusters:
            r = self.get_clusters_word_cloud(cluster_model_id, c)
            with open( "{}{:02d}.png".format(file_prefix, c), 'wb') as f:
                f.write(r.content)
