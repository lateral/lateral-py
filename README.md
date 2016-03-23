# Installation

git clone https://github.com/lateral/apiwrappy.git
pip install -e ./src

# Usage

All api calls, but the batch call, are available in the api.Api class. They are somehow canonically derived from https://lateral.io/docs/api/
such that the endpoint translates to a funciton name. Text parameters have to be passed as string and json parameters as python dictionary.

Example
```
from lateral import api

api = api.Api(key='YOUR_API_WRITE_KEY')

r = api.post_document("This is a text to be stored in my document base.")
r = api.get_documents("document base")
```

There is also a class loader.ApiLoader meant to batch insert documents stored as csv file into the api. It demonstrates how to compose data for batch calls, which are faster, especially if you insert many small documents.
