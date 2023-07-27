from image_to_bom.image2bom import image2bom
import json
import re
import os
import uuid
import datetime
import time

class CompareImagePerformance:

    global formatted_datetime
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ") 

    def __init__(self):
        self.image2bom = image2bom

    def get_data(self, fp1, fp2):
        """
        Retreives eithe prelabled data or image2BOM results for image.

        fp1: fp for to image be ran in image2bom 
        fp2: gp for pre-labeled data on the same image
        """
        BOM_results = image2bom(fp1)
        with open(fp2) as file:
            json_data = file.read()
        known_Data = json.loads(json_data)
        return BOM_results["bom"]["rows"], known_Data[0]['boundingBoxes']

    def check_bb_overlap(self, bb_i, bb_j, iou_overlap: float = 0.1, min_overlap: float = 0.75):
        """
        Checks for bounding box overlap and returns boolean result.

        bb_i: bb of image2bom result
        bb_j: bb of labeled image
        iou overlap: margin of accuracy 
        min_overlap: minimum IOU to be considered the same bb

        *** Borrowed from Alexander's Image2BOM ulil.py class ***
        """
        xi0, yi0, xi1, yi1 = bb_i
        xj0, yj0, xj1, yj1 = bb_j

        width_i = xi1 - xi0
        height_i = yi1 - yi0
        area_i = width_i * height_i

        width_j = xj1 - xj0
        height_j = yj1 - yj0
        area_j = width_j * height_j

        difx = min(xi1 - xj0, xj1 - xi0)
        dify = min(yi1 - yj0, yj1 - yi0)
        
        if difx > 0 and dify > 0:
            width_j = xj1 - xj0
            height_j = yj1 - yj0
            area_j = width_j * height_j
            intersectionx = min(difx, width_i, width_j)
            intersectiony = min(dify, height_i, height_j)
            intersection = intersectionx * intersectiony
            if (
                intersection / (area_i + area_j - intersection) > iou_overlap
            ) or (intersection / min(area_i, area_j) > min_overlap):
                return True
        return False

    def get_component_type(self, component):
        """
        Splits labeled data and converts it to long name to compare with data found by image2bom.

        component: labeled data component structured as CHARnbr
        """
        componentDict = {
            "S": "button/switch",
            "U": "IC",
            "L": "inductor",
            "R": "resistor",
            "SW": "button/switch",
            "BTN": "button",
            "J": "other_interface",
            "C": "capacitor",
            "CN": "capacitor",
            "EM": "capacitor",
            "VC": "capacitor",
            "L": "inductor",
            "FEB": "inductor",
            "FB": "inductor",
            "D": "diode",
            "DA": "diode",
            "CR": "diode",
            "Z": "diode",
            "IR": "diode",
            "Q": "transistor",
            "M": "transistor",
            "T": "transformer",
            "LD": "LED",
            "LA": "LED",
            "LED": "LED",
            "LCD": "LED",
            "J": "pins",
            "JP": "pins",
            "X": "crystal/oscillator",
            "Y": "crystal/oscillator",
            "XTAL": "crystal/oscillator",
            "G": "crystal/oscillator",
            "RLA": "relay",
            "RY": "relay",
            "K": "relay",
            "F": "fuse",
            "EC": "capacitor",
            "XF": "fuse holder",
            "OSC": "oscillator",
            "B": "button"
        }
        result = re.split(r'(\d+)', component)
        short_name = ""
        for char in result: 
            if not char.isdigit():
                short_name += char
        try:
            full_name = componentDict[short_name]
        except KeyError:
            print("KEY NOT FOUND: " + str(short_name))
            return None
        return full_name

    def find_best_match(self, labeled_BOM_results, BB, Type, label_match = 2, bb_match = 4, type_match = 1, label=None):
        """
        Determines the best match for a image2BOM result by looping through labeled data and comparing
        characteristics including their bounding boxes, type (long name), label (short name).

        The highest scored match is considered the best match ... the index of this match and the score 
        are returned in a list formant. 

        Scoring is subject and can be changed by the parameters label_match, bb_match, type_match, but have default
        values that prioritize matching bounding boxes, then labels, then type.

        BB = bounding box of image2BOM result
        Type = type (long name) of image2BOM result
        label = label (short name) of image2BOM result, defualt set to None
        """    
        bestMatch = [-1, -1]
        for known_index, known_component in enumerate(labeled_BOM_results):
            bb_2 = [known_component["x0"], known_component["y0"], known_component["x1"], known_component["y1"]]
            score = 0
            labeled_type = self.get_component_type(known_component["label"])
            if labeled_type is None: continue
            else: 
                if Type == labeled_type: score += type_match
                bb_matches = self.check_bb_overlap(BB, bb_2)
                if bb_matches: score += int(bb_match)
                if label is not None and label == known_component: score += label_match
                if bestMatch [1] < score: bestMatch = [known_index, score]
        return bestMatch
    
    def get_match_list(self, BOM_results, labeled_BOM_results, result_dict):
        """
        Collects a list of all the best matches for boxes and tallies the type of each result in a dictionary.
        Each type is a unique combination of the three different potential matches. 

        result_dict: holds frequency of result combination types
        """ 
        labeled_index_list = []
        total_score = 0
        for BOM_component in BOM_results:
            BOM_type = BOM_component[0]
            BOM_bb = BOM_component[1]
            BOM_label = BOM_component[3]

            best_match_found = self.find_best_match(labeled_BOM_results, BOM_bb, BOM_type, BOM_label)
            total_score += best_match_found[1]
            if best_match_found[1] == -1:
                result_dict["noMatchFound"] += 1
            elif best_match_found[1] == 1:
                result_dict["type_match"] += 1
            elif best_match_found[1] == 4:
                result_dict["bb_match"] += 1
            elif best_match_found[1] == 5:
                result_dict["type_and_bb_match"] += 1
            elif best_match_found[1] == 2:
                result_dict["label_match"] += 1
            elif best_match_found[1] == 3:
                result_dict["type_and_label_match--"] += 1
            elif best_match_found[1] == 6:
                result_dict["type_and_bb_match"] += 1
            elif best_match_found[1] == 7:
                result_dict["perfectMatch"] += 1
            else:
                print("NO RESULT FOUND. UNKNOWN COMPONENT: " + str(BOM_component))

                    
            if (best_match_found[1] > 1):labeled_index_list.append(best_match_found[0])
        return total_score
    
    def change_results(self, unknownn_length, known_length, total_score, result_dict, time_input):
        """
        Computes different metrics to quantify the results and describe model performance.
        Formats the computations for visual understanding in output.json file.

        unknown_length: number of components in image2BOM result
        known_length: number of compenents in labeled data 
        total_score: sum of scores match scores
        result_dict: frequency of each match combination type
        """
        results = {}
        other_information = {}
        time2 = time.time()

        results["other_information"] = other_information

        results["id"] = str(uuid.uuid4())

        other_information["image2bom_result_length"] = str(unknownn_length)
        other_information["labeled_result_length"] = str(known_length)

        max_score = 7 * known_length
        other_information["maximum_potential_score"] = str(max_score)
        other_information["image2bom_score"] = str(total_score)
        results["overall_score"] = str('%.3f'%((total_score/max_score)*100))


        other_information["no_match_found"] = str(result_dict["noMatchFound"])
        other_information["type_match"] = str(result_dict["type_match"])
        other_information["box_match"] = str(result_dict["bb_match"])
        other_information["label_match"] = str(result_dict["label_match"])
        other_information["type/box_match"] = str(result_dict["type_and_bb_match"])
        other_information["type/label_match"] = str(result_dict["type_and_label_match"])
        other_information["box/label_match"] = str(result_dict["box_and_label_match"])
        other_information["complete_match"] = str(result_dict["perfectMatch"])


        positive_results = result_dict["perfectMatch"] + result_dict["box_and_label_match"] + result_dict["type_and_bb_match"]
        negative_results = unknownn_length - positive_results

        results["positive_result"] = str('%.3f'%((positive_results/unknownn_length)*100))
        other_information["negative_result"] = str('%.3f'%((negative_results/unknownn_length)*100)) 

        other_information["label_accuracy"] = str('%.3f'%(((result_dict["label_match"] + result_dict["box_and_label_match"] + result_dict["type_and_label_match"])/unknownn_length)*100))
        results["BB_accuracy"] = str('%.3f'%(((result_dict["box_and_label_match"] + result_dict["bb_match"] + result_dict["type_and_bb_match"])/unknownn_length)*100))
        curtime = str('%.3f'%(time2 - float(time_input)))
        results["time"]  = curtime
        return results, curtime
    
    def create_result_dict(self):
        """
        Creates a new result dicitonary everytime image2BOM is run on a new image
        """
        result_dict = {
            "noMatchFound": 0,
            "type_match": 0,
            "bb_match": 0,
            "label_match": 0,
            "type_and_bb_match": 0,
            "type_and_label_match": 0,
            "box_and_label_match": 0,
            "perfectMatch": 0
        }
        return result_dict
    
    def runTest(self, fp1, fp2, time):
        """
        Runs the test for comparing image2BOM and labeled results give two specified path names.
        Calls the helper methods to do so.

        fp1: image run in image2BOM
        fp2: labeled results for same image
        """
        BOM_results, labeled_BOM_results = self.get_data(fp1, fp2)
        result_dict = self.create_result_dict()
        total_score = self.get_match_list(BOM_results, labeled_BOM_results, result_dict)
        results = self.change_results(len(BOM_results), len(labeled_BOM_results), total_score, result_dict, time)    
        return results
        

    def compare_image_performance(self):
        """
        Serves as "main" method and calls runTest on different sets of data.
        Also keeps track of how long it takes to run the test on each set of data
        and formats/prints results to the console.
        """
        results = {}
        results["@timestamp"] = formatted_datetime

        start = time.time()
        small1 = "../image_to_bom_test/bom2image_test_photos/small_board/small.jpg"
        small2 = "../image_to_bom_test/bom2image_test_photos/small_board/small_labels.json"
        result, time_returned = self.runTest(small1, small2, start)
        results["small"] = result

        medium1 = "../image_to_bom_test/bom2image_test_photos/medium_board/medium.jpg"
        medium2 = "../image_to_bom_test/bom2image_test_photos/medium_board/medium_labels.json"
        result, time_returned = self.runTest(medium1, medium2, time_returned)
        results["medium"] = result

        large1 = "../image_to_bom_test/bom2image_test_photos/large_board/large.jpg"
        large2 = "../image_to_bom_test/bom2image_test_photos/large_board/large_labels.json"
        result  = self.runTest(large1, large2, time_returned)
        results["large"] = result[0]

        return results
    
    # Example run of compare_image_performance
    def create_output_file(self, data = None):
        """
        If "output.json" exists, results are appended to the jsonl object
        If "output.json" does not exit, the file is create and results are dumped in a jsonl format.

        data: optional parameter for selecting data to be added to "output.son". Default is image2BOM results
        
        """
        if data is not None: results = data
        else: results = self.compare_image_performance()

        fp = 'output.json'
        if not os.path.isfile(fp):
            initial_data = {'my_list': []}

            with open(fp, 'w') as file:
                json.dump(initial_data, file, indent=4)

        with open(fp, 'r') as file:
            data = json.load(file)

        if 'my_list' not in data or not data['my_list']:
            data['my_list'] = []

        data['my_list'].append(results)
        with open(fp, 'w') as file:
            json.dump(data, file, indent=4)


if __name__ == "__main__":
    instance =  CompareImagePerformance()
    instance.create_output_file()