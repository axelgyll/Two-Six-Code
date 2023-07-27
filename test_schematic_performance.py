import unittest
import schematic_construction_util
import elastic_search_util
import datetime
import s3_bucket_util

class testSchematicPerformance(unittest.TestCase):  
    def getTotalDifference(self, counts):
        print( "COUNT[0] " + str(counts[0]))
        total_differences = []
        for original, new in zip(counts[0][0], counts[0][1]):
            total_differences.append(abs(original-new))
        return total_differences

    def formatResult(self, demo = None, kicad_counts=None, kicad_image_paths=None, altium_counts=None, altium_image_paths=None):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ") 

        kicad_count_difference_boxes, kicad_count_difference_wires, kicad_count_difference_junctions = self.getTotalDifference(kicad_counts)
        altium_count_difference_boxes, altium_count_difference_wires, altium_count_difference_junctions = self.getTotalDifference(altium_counts)
        
        if demo is not None: formatted_datetime = demo

        count_result = {
            "@timestamp": formatted_datetime,
            "kicad_total_difference": {
                "kicad_count_difference_boxes": kicad_count_difference_boxes,
                "kicad_count_difference_wires": kicad_count_difference_wires,
                "kicad_count_difference_junctions": kicad_count_difference_junctions
            },
            "altium_total_difference": {
                "altium_count_difference_boxes": altium_count_difference_boxes,
                "altium_count_difference_wires": altium_count_difference_wires,
                "altium_count_difference_junctions": altium_count_difference_junctions
            },
            "kicad_count": {
                "one": {
                    "original": kicad_counts[0][0],
                    "new": kicad_counts[1][0]
                },
                "two": {
                    "original": kicad_counts[0][1],
                    "new": kicad_counts[1][1]
                },
                "three": {
                    "original": kicad_counts[0][2],
                    "new": kicad_counts[1][2]
                }
            },
            "altium_count": {
                "one": {
                    "original": altium_counts[0][0],
                    "new": altium_counts[1][0]
                },
                "two": {
                    "original": altium_counts[0][1],
                    "new": altium_counts[1][1]
                },
                "three": {
                    "original": altium_counts[0][2],
                    "new": altium_counts[1][2]
                }
            }
        }
        
        list = kicad_image_paths[0] + kicad_image_paths[1] + altium_image_paths[0] + altium_image_paths[1]

        image_result = {
            "@timestamp": formatted_datetime,
            "s3_bucket_link": "terrible-test-bucket-cf1e2cb0-76a1-47dc-b3d5-9298dd99d4dc/schematic_testing/",
            "s3_image_links": list
        }        

        return count_result, image_result
    
    def getDemoData(self):
        kicad_image_paths = [['schematic_cv_test/data/original_test_data/kicad_png/oldkicad1.png', 'schematic_cv_test/data/original_test_data/kicad_png/oldkicad2.png', 'schematic_cv_test/data/original_test_data/kicad_png/oldkicad3.png'], ['/home/anders/schematic-cv/schematic_cv_test/data/new_test_data/kicad_png/newkicad1.png', '/home/anders/schematic-cv/schematic_cv_test/data/new_test_data/kicad_png/newkicad2.png', '/home/anders/schematic-cv/schematic_cv_test/data/new_test_data/kicad_png/newkicad3.png']]
        altium_image_paths = [['schematic_cv_test/data/original_test_data/altium_png/oldaltium1.png', 'schematic_cv_test/data/original_test_data/altium_png/oldaltium2.png', 'schematic_cv_test/data/original_test_data/altium_png/oldaltium3.png'], ['/home/anders/schematic-cv/schematic_cv_test/data/new_test_data/altium_png/newaltium1.png', '/home/anders/schematic-cv/schematic_cv_test/data/new_test_data/altium_png/newaltium2.png', '/home/anders/schematic-cv/schematic_cv_test/data/new_test_data/altium_png/newaltium3.png']]
        demo =[
                [[[[192, 904, 56], [228, 596, 84], [292, 120, 36]], [[192, 1200, 24], [148, 1628, 140], [216, 596, 20]]], [[[208, 456, 96], [32, 104, 12], [136, 264, 32]], [[208, 816, 80], [124, 340, 8], [112, 880, 60]]], "2023-04-14T15:10:14Z"],
                [[[[144, 678, 42], [171, 447, 63], [219, 90, 27]],[[144, 900, 18], [111, 1221, 105], [162, 447, 15]]], [[[156, 342, 72], [24, 78, 9], [102, 198, 24]], [[156, 612, 60], [93, 255, 6], [84, 660, 45]]], "2023-05-14T15:10:14Z"], 
                [[[[96, 452, 28], [114, 298, 42], [146, 60, 18]], [[96, 600, 12], [74, 814, 70], [108, 298, 10]]], [[[104, 228, 48], [16, 52, 6], [68, 132, 16]], [[104, 408, 40], [62, 170, 4], [56, 440, 30]]], "2023-06-14T15:10:14Z"]
            ]

        result = []
        for count in demo:
            count_results, image_results = self.formatResult(
                                demo = count[2],
                                kicad_counts=count[0], 
                                kicad_image_paths=kicad_image_paths, 
                                altium_counts=count[1], 
                                altium_image_paths= altium_image_paths,
                                ) 
            result.append([count_results, image_results])
        return result

    def testPerformance(self):
        schematic_construction_handler = schematic_construction_util.SchematicConstruction()

        kicad_sch_files = ["schematic_cv_test/data/original_test_data/kicad_sch/kicad1.kicad_sch", 
                    "schematic_cv_test/data/original_test_data/kicad_sch/kicad2.kicad_sch",
                    "schematic_cv_test/data/original_test_data/kicad_sch/kicad3.kicad_sch"]
        
        altium_sch_files = ["schematic_cv_test/data/original_test_data/altium_sch/altium1.SchDoc",
                    "schematic_cv_test/data/original_test_data/altium_sch/altium2.SchDoc",
                    "schematic_cv_test/data/original_test_data/altium_sch/altium3.SchDoc"
        ]
        
        kicad_counts, kicad_image_paths = schematic_construction_handler.run_test(kicad_sch_files, "kicad")
        altium_counts, altium_image_paths = schematic_construction_handler.run_test(altium_sch_files, "altium")

        count_results, image_results = self.formatResult(
                                        kicad_counts=kicad_counts, 
                                        kicad_image_paths=kicad_image_paths, 
                                        altium_counts=altium_counts, 
                                        altium_image_paths= altium_image_paths,
                                        )
        
        username = "axel"
        password = "changeme"
        cloud_id = "https://aegean-data-t4g-medium-1.averagearcher.net:9200"
        data_stream_counts = "performance-data-schematics-counts"
        data_stream_images = "performance-data-schematics-images"
        s3_bucket = "terrible-test-bucket-cf1e2cb0-76a1-47dc-b3d5-9298dd99d4dc"

        es_handler = elastic_search_util.ElasticSearchHandler(cloud_id, username, password)

        if not es_handler.es.ping(): raise BaseException("Connection failed")
        es_handler.delete_data_stream(data_stream_counts)
        es_handler.delete_data_stream(data_stream_images)
        es_handler.create_data_stream(data_stream_counts)
        es_handler.create_data_stream(data_stream_images)

        demo_data = self.getDemoData()

        for demo in demo_data:
            es_handler.add_document(data_stream_counts, demo[0])

        es_handler.add_document(data_stream_counts, count_results)
        es_handler.add_document(data_stream_images, image_results)

        local_image_paths = image_results["s3_image_links"]

        for image in local_image_paths:
            desired_object_key = "schematic_testing/" + image_results["@timestamp"] + "/" + image.split("/")[-1]
            s3_bucket_util.addToS3Bucket(image, s3_bucket, desired_object_key)

        folder_key = "schematic_testing/" + image_results["@timestamp"]
        s3_bucket_util.downloadAndCreateHTML(s3_bucket, folder_key)

if __name__ == "__main__":
    unittest.main()