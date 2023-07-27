import unittest
from image_to_bom_test.performance_tests.compare_image_performance import CompareImagePerformance
from elastic_searching_util import ElasticSearchHandler
import colorama

class TestPerformanceDeterioration(unittest.TestCase):
    def test_performance_deterioration(self):
        import_statistics = ["overall_score", "positive_result", "BB_accuracy"]
        sizes = ["small", "medium", "large"]

        username = "axel"
        password = "changeme"
        cloud_id = "https://aegean-data-t4g-medium-1.averagearcher.net:9200"
        data_stream = "performance-data-image2bom"

        es_handler = ElasticSearchHandler(cloud_id, username, password)
        compare_image_performance = CompareImagePerformance()

        # check connection
        try:
            if not es_handler.es.ping(): raise BaseException("Connection failed")
        except BaseException: 
            print(colorama.Fore.RED + "FAILED TO ESTABLISH CONNECTION TO ES" + colorama.Fore.RESET)
            self.assertFalse(1)

        current_record = compare_image_performance.compare_image_performance()
        """current_record = {
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
                "overall_score": "0",
                "positive_result": "84.848",
                "BB_accuracy": "87.879",
                "time": "150.351"
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
                "overall_score": "8.484",
                "positive_result": "78.378",
                "BB_accuracy": "97.297",
                "time": "1689361898.927"
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
                "id": "b43853bf-e77c-4652-a642-63536e229d4b",
                "overall_score": "7.519",
                "positive_result": "65.385",
                "BB_accuracy": "92.308",
                "time": "340.224"
            }
        }"""
        last_record = es_handler.search_most_recent(data_stream)

        # if int then an error occured, create new index
        if isinstance(last_record, int):
            if last_record == -1: 
                es_handler.create_data_stream(data_stream)
                print(colorama.Fore.GREEN + "SUCESSFULLY CREATED NEW ES INDEX" + colorama.Fore.RESET)
        
        else:
            errors = []
            for size in sizes: 
                    for cur_metric in import_statistics:
                        if (cur_metric in current_record[size] and cur_metric in last_record[size]):
                            last_cur_metric = last_record[size][cur_metric]
                            cur_cur_metric = current_record[size][cur_metric]
                            threshold = 0.95 * float(last_cur_metric)
                            if float(cur_cur_metric) <= threshold:
                                errors.append([size, cur_metric])
                        else:
                            print(colorama.Fore.RED + "Invalid keys (" + str(size) + ", " + str(cur_metric) + ", " + str(last_cur_metric) + ", " + str(cur_cur_metric) + ") in dictionaries" + colorama.Fore.RESET)

            if len(errors):
                for error in errors:
                    print(colorama.Fore.RED + "PERFORMANCE DETERIORATION in size " + str(error[0]) + ", cur_metric " + str(error[1]) + colorama.Fore.RESET)
                self.assertFalse(1)

        es_handler.add_document(data_stream, current_record)
        print(colorama.Fore.GREEN + "SUCCESSFULLY ADDED NEW RECORD TO ES" + colorama.Fore.RESET)
        self.assertTrue(1)

if __name__ == '__main__':
    unittest.main()
