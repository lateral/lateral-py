# Lateral.py

Python client library for using the Lateral API.

![Lateral pie](https://i.imgur.com/464Q4vB.jpg)

## Installation

```bash
git clone https://github.com/lateral/lateral.py.git
pip install requests responses
pip install -e ./
```

## Usage

All api calls, but the batch call, are available in the api.Api class.

Function names are derived from the definition https://lateral.io/docs/api/ such that the endpoint translates to an url. For GET, PUT and POST of single entities the plural `s` is omitted and for clusters functions the first component is dropped.

Text parameters have to be passed as string and json parameters as python dictionary.

## Example

```python
from lateral import api

api = api.Api(key='YOUR_API_WRITE_KEY')

r = api.post_document("This is a text to be stored in my document base.")
r = api.get_documents("document base")
```

There is also a class loader.ApiLoader with a function to batch insert documents stored as csv file into the api. It demonstrates how to compose data for batch calls, which are faster, especially if you insert many small documents.
