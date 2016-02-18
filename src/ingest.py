#!/usr/bin/python
import requests
import csv
import json

datafile = '../data/news_test.csv'

url = "http://104.155.50.80/documents"

headers = {
    'subscription-key': "ee9b64acf288f20816ecfbbd20db1560",
    'content-type': "application/json"
    }

def tagcols(arr):
    return arr[1:6]

def textcol():
    return 0

with open(datafile, 'rb') as csvfile:
    newsreader = csv.reader(csvfile, quotechar='"')
    header = newsreader.next()
    print(header)

    success_cnt = 0
    failed_cnt = 0

    for row in newsreader:
        # print(row)
        d = dict()

        d['text'] = row[textcol()]
        meta = dict()
        meta['title'] = "hallo"
        for i, c in enumerate(tagcols(row)):
            meta[tagcols(header)[i]] = c
        d['meta'] = json.dumps(meta)

        response = requests.request("POST", url, headers=headers, data=json.dumps(d))
        success_cnt += 1

        # print(d)
        print(response.text)

    print(header)

