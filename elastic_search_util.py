import datetime
import warnings
import webbrowser
import colorama
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import urllib3
import s3_bucket_util


class ElasticSearchHandler:
    def __init__(self, cloud_id, username, password):
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        self.es = Elasticsearch(cloud_id, basic_auth=(username, password), verify_certs=False)

    def create_data_stream(self, data_stream):
        index_pattern = f'{data_stream}-*'

        data_stream_config = {
            'name': data_stream,
            'indices': [
                {
                    'index': index_pattern
                }
            ]
        }

        try:
            self.es.indices.create_data_stream(name=data_stream, body=data_stream_config)
        except es_exceptions.BadRequestError as e:
            print (colorama.Fore.RED + "ERROR in creating data stream: data_stream " + str(data_stream) + " already exists")
            print("Process continuing" + colorama.Fore.RESET)

    def delete_data_stream(self, data_stream):
        try:
            self.es.indices.delete_data_stream(name=data_stream)
            print(f"Data stream '{data_stream}' deleted successfully.")
        except es_exceptions.NotFoundError:
            print(f"Data stream '{data_stream}' not found.")

    def add_document(self, data_stream, document):
        try: 
            self.es.index(index=data_stream, body=document, error_trace=True)
        except es_exceptions.BadRequestError as e:
            print(e.info)
            exit()

        self.es.indices.refresh(index=data_stream)

    def search_most_recent(self, index_name):
        try: 
            search_query = {
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {
                        "@timestamp": {
                            "order": "desc"
                        }
                    }
                ],
                "size": 1
            }
            most_recent_document = self.es.search(index=index_name, body=search_query)
        except es_exceptions.NotFoundError: return -1

        if most_recent_document["hits"]["total"]["value"] > 0:
            most_recent_document = most_recent_document["hits"]["hits"][0]["_source"]
            return most_recent_document
        else:
            return -2
    
    def example_run(self):
        username = "axel"
        password = "changeme"
        cloud_id = "https://aegean-data-t4g-medium-1.averagearcher.net:9200"
        data_stream = "performance-data-schematics"

        es_handler = ElasticSearchHandler(cloud_id, username, password)

        if not es_handler.es.ping(): raise BaseException("Connection failed")
        es_handler.create_data_stream(data_stream)
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")  

        result1 = {
                "@timestamp": "2023-05-14T15:10:14Z",
                "kicad_count": {
                    "one": {
                        "original": [48, 226, 14],
                        "new": [48, 300, 6]
                    },
                    "two": {
                        "original": [57, 149, 21],
                        "new": [37, 407, 35]
                    },
                    "three": {
                        "original": [73, 30, 9],
                        "new": [54, 149, 5]
                    }
                },
                "altium_count": {
                    "one": {
                        "original": [48, 226, 14],
                        "new": [48, 300, 6]
                    },
                    "two": {
                        "original": [57, 149, 21],
                        "new": [37, 407, 35]
                    },
                    "three": {
                        "original": [73, 30, 9],
                        "new": [54, 149, 5]
                    }
                }
            }

        es_handler.add_document(data_stream, result1)