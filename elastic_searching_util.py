import datetime
import warnings
import colorama
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import urllib3


class ElasticSearchHandler:
    def __init__(self, cloud_id, username, password):
        """
        Supresses warnings to console (insecure bc of no SSL certifcate check and worrying about deprecated tools later).
        Initialize elastic search instance.

        cloud_id: where data is being sent/pulled from
        username & password: credentials for login
        """
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
            print (colorama.Fore.RED + "ERROR in creating data stream: data_stream " + str(data_stream) + " already exists" + colorama.Fore.RESET)

    def delete_data_stream(self, data_stream):
        try:
            self.es.indices.delete_data_stream(name=data_stream)
            print(f"Data stream '{data_stream}' deleted successfully.")
        except es_exceptions.NotFoundError:
            print(f"Data stream '{data_stream}' not found.")

    def add_document(self, data_stream, document):
        """
        Add document to index_name
        """

        try: 
            self.es.index(index=data_stream, body=document, error_trace=True)
        except es_exceptions.BadRequestError as e:
            print(e.info)
            exit()

        self.es.indices.refresh(index=data_stream)

    def search_most_recent(self, index_name):
        """
        Find the most recent data entry in the index_name index by looking at descending
        timestamps. If an error occurs return integer that specifies the reason for the error ...
        -1 = the index does not exist
        -2 = the index holds no entries
        """
        try: 
            search_query = {
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {
                        "timestamp": {
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


# Example usage
if __name__ == "__main__":
    username = "axel"
    password = "changeme"
    cloud_id = "https://aegean-data-t4g-medium-1.averagearcher.net:9200"
    data_stream = "performance-data-image2bom"

    es_handler = ElasticSearchHandler(cloud_id, username, password)

    if not es_handler.es.ping(): raise BaseException("Connection failed")
    es_handler.delete_data_stream(data_stream)
    es_handler.create_data_stream(data_stream)
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")  # For "YYYY-MM-DDTHH:MM:SSZ" format

    result1 = {
    "@timestamp": "2023-05-14T15:10:14Z",
    "small": {
        "other_information": {
            "image2bom_result_length": "33",
            "labeled_result_length": "34",
            "maximum_potential_score": "238",
            "image2bom_score": "145",
            "no_match_found": "0",
            "type_match": "1",
            "box_match": "1",
            "label_match": "0",
            "type/box_match": "28",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "15.152",
            "label_accuracy": "0.000"
            },
        "id": "64c800b8-a8f2-4bd6-afd2-cd02f45014bb",
        "overall_score": 10.308,
        "positive_result": 14.283,
        "BB_accuracy": 14.626,
        "time": 600.702
        },
    "medium": {
        "other_information": {
            "image2bom_result_length": "37",
            "labeled_result_length": "293",
            "maximum_potential_score": "2051",
            "image2bom_score": "174",
            "no_match_found": "0",
            "type_match": "1",
            "box_match": "7",
            "label_match": "0",
            "type/box_match": "29",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "21.622",
            "label_accuracy": "0.000"
            },
        "id": "9ffbc1ed-7651-4d6e-bcaf-c0ec0680b4f5",
        "overall_score": 1.494,
        "positive_result": 13.126,
        "BB_accuracy": 15.099,
        "time": 5378723797.854
    },
    "large": {
            "other_information": {
            "image2bom_result_length": "52",
            "labeled_result_length": "437",
            "maximum_potential_score": "3059",
            "image2bom_score": "230",
            "no_match_found": "0",
            "type_match": "4",
            "box_match": "14",
            "label_match": "0",
            "type/box_match": "34",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "34.615",
            "label_accuracy": "0.000"
            },
        "id": "b43953bf-e77c-4652-a642-63536e229d4b",
        "overall_score": 1.173,
        "positive_result": 11.795,
        "BB_accuracy": 14.103,
        "time": 1280.448
        }
    }

    result2 = {
    "@timestamp": "2023-06-14T15:10:14Z",
        "small": {
            "other_information": {
            "image2bom_result_length": "33",
            "labeled_result_length": "34",
            "maximum_potential_score": "238",
            "image2bom_score": "145",
            "no_match_found": "0",
            "type_match": "1",
            "box_match": "1",
            "label_match": "0",
            "type/box_match": "28",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "15.152",
            "label_accuracy": "0.000"
        },
        "id": "64c800b8-a8f2-4bd6-afd2-cd02f45014bb",
        "overall_score": 20.308,
        "positive_result": 28.283,
        "BB_accuracy": 29.293,
        "time": 300.702
        },
    "medium": {
        "other_information": {
            "image2bom_result_length": "37",
            "labeled_result_length": "293",
            "maximum_potential_score": "2051",
            "image2bom_score": "174",
            "no_match_found": "0",
            "type_match": "1",
            "box_match": "7",
            "label_match": "0",
            "type/box_match": "29",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "21.622",
            "label_accuracy": "0.000"
        },
        "id": "9ffbc1ed-7651-4d6e-bcaf-c0ec0680b4f5",
        "overall_score": 2.828,
        "positive_result": 26.126,
        "BB_accuracy": 32.092,
        "time": 4078723797.854
        },
    "large": {
        "other_information": {
            "image2bom_result_length": "52",
            "labeled_result_length": "437",
            "maximum_potential_score": "3059",
            "image2bom_score": "230",
            "no_match_found": "0",
            "type_match": "4",
            "box_match": "14",
            "label_match": "0",
            "type/box_match": "34",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "34.615",
            "label_accuracy": "0.000"
        },
        "id": "b43953bf-e77c-4652-a642-63536e229d4b",
        "overall_score": 2.507,
        "positive_result": 21.795,
        "BB_accuracy": 30.103,
        "time": 600.448
        }
    }

    result3 = {
    "@timestamp": "2023-07-14T15:10:14Z",
    "small": {
        "other_information": {
            "image2bom_result_length": "33",
            "labeled_result_length": "34",
            "maximum_potential_score": "238",
            "image2bom_score": "145",
            "no_match_found": "0",
            "type_match": "1",
            "box_match": "1",
            "label_match": "0",
            "type/box_match": "28",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "15.152",
            "label_accuracy": "0.000"
        },
        "id": "64c800b8-a8f2-4bd6-afd2-cd02f45014bb",
        "overall_score": 30.308,
        "positive_result": 34.949,
        "BB_accuracy": 42.626,
        "time": 175.702
    },
    "medium": {
        "other_information": {
            "image2bom_result_length": "37",
            "labeled_result_length": "293",
            "maximum_potential_score": "2051",
            "image2bom_score": "174",
            "no_match_found": "0",
            "type_match": "1",
            "box_match": "7",
            "label_match": "0",
            "type/box_match": "29",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "21.622",
            "label_accuracy": "0.000"
        },
        "id": "9ffbc1ed-7651-4d6e-bcaf-c0ec0680b4f5",
        "overall_score": 4.161,
        "positive_result": 33.459,
        "BB_accuracy": 50.099,
        "time": 2078723797.854
    },
    "large": {
        "other_information": {
            "image2bom_result_length": "52",
            "labeled_result_length": "437",
            "maximum_potential_score": "3059",
            "image2bom_score": "230",
            "no_match_found": "0",
            "type_match": "4",
            "box_match": "14",
            "label_match": "0",
            "type/box_match": "34",
            "type/label_match": "0",
            "box/label_match": "0",
            "complete_match": "0",
            "negative_result": "34.615",
            "label_accuracy": "0.000"
        },
        "id": "b43953bf-e77c-4652-a642-63536e229d4b",
        "overall_score": 4.839,
        "positive_result": 31.795,
        "BB_accuracy": 40.103,
        "time": 400.448
    }
    }

    es_handler.add_document(data_stream, result1)
    es_handler.add_document(data_stream, result2)
    es_handler.add_document(data_stream, result3)