import datetime

from cairosvg import svg2png

from schematic_cv.schematic_scanner import SchematicScanner
from schematic_toolkit.kicad.sch import KiCADSchematic
from schematic_toolkit.altium.sch import AltiumSchematic
from schematic_toolkit.core.reconstruct.util import ScannedSchematic
from schematic_toolkit.altium import util
from schematic_toolkit.altium.defs import RecordType
from schematic_toolkit.ingest import read_sch


class SchematicConstruction:
    def readSchFile(self, file):
        return read_sch(file)

    def getTypeCounts(self, sch, sch_type):
        bboxes = len(sch.get_symbol_bboxes()[0])
        if sch_type == "kicad":
            wire_list = len(sch.repr.wire)
            junction_list = len(sch.repr.junction)
        else: 
            wire_list = len(util.get_records_type(sch.repr.sheet, RecordType.WIRE))
            junction_list = len(util.get_records_type(sch.repr.sheet, RecordType.JUNCTION))
        return [bboxes, wire_list, junction_list]


    def buildSchImages(self, sch_files, sch_type):
        schematics, filenames = [], []
        for file in sch_files: 
            sch = read_sch(file)
            schematics.append(sch)
            filename = file.split("/")[-1]
            if sch_type == "kicad": new_filename = "schematic_cv_test/data/original_test_data/kicad_png/old" + filename.replace(".kicad_sch", ".png")
            else: new_filename = "schematic_cv_test/data/original_test_data/altium_png/old" + filename.replace(".SchDoc", ".png")
            filenames.append(new_filename)
            sch.to_png((new_filename), overwrite = True)

        return schematics, filenames
    
    def scanNewSchImages(self, image_paths, sch_type): 
        scanner = SchematicScanner(1)
        sch_list = []
        for image_path in image_paths:
            scanned_sch = scanner.scan(image_path)
            if (sch_type == "kicad"): sch = KiCADSchematic.reconstruct(ScannedSchematic.from_cv(scanned_sch))
            else: sch = AltiumSchematic.reconstruct(ScannedSchematic.from_cv(scanned_sch))
            sch_list.append(sch)
        return sch_list
    
    def reconstructSchImage(self, sch_list, sch_files, sch_type):
        kicad_format = "kicad_sch"
        altium_format = "SchDoc"
        
        new_image_paths = []
        for sch, file in zip(sch_list, sch_files): 
            name_prefix = "schematic_cv_test/data/new_test_data/"
            if (sch_type == "kicad"): 
                name = ("new" + file.split("/")[-1]).replace("." + kicad_format, "")
                sch.save(name_prefix + kicad_format + "/" + name + "_reconstructed.hide." + kicad_format, overwrite=True)
            else: 
                name = ("new" + file.split("/")[-1]).replace("." + altium_format, "")
                sch.save(name_prefix + altium_format + "/" + name + "_reconstructed.hide." + altium_format, overwrite=True)

            sch.to_svg(name_prefix + sch_type +"_svg/" + name + "_reconstructed.hide.svg", overwrite=True)
            input_svg_file = "/home/anders/schematic-cv/" + name_prefix + sch_type + "_svg/" + name + "_reconstructed.hide.svg"
            output_png_file = "/home/anders/schematic-cv/" + name_prefix + sch_type + "_png/" + name + ".png"
            svg2png(url=input_svg_file, write_to=output_png_file)
            new_image_paths.append(output_png_file)
        return new_image_paths
    
    def formatReselts(self, original_count_kicad, new_count_kicad, original_count_altium, new_count_altium):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        result = {
            "@timestamp": formatted_datetime,
            "kicad": {
                "one": {
                    "original": original_count_kicad[0],
                    "new": new_count_kicad[0]
                },
                "two": {
                    "original": original_count_kicad[1],
                    "new": new_count_kicad[1]
                },
                "three": {
                    "original": original_count_kicad[2],
                    "new": new_count_kicad[2]
                }
            },
            "altium": {
                "one": {
                    "original": original_count_altium[0],
                    "new": new_count_altium[0]
                },
                "two": {
                    "original": original_count_altium[1],
                    "new": new_count_altium[1]
                },
                "three": {
                    "original": original_count_altium[2],
                    "new": new_count_altium[2]
                }
            }
        }

        return result
    
    def run_test(self, files, sch_type):
        schematics, image_paths = self.buildSchImages(files, sch_type)
        original_count = []
        for sch in schematics: original_count.append(self.getTypeCounts(sch, sch_type))

        sch_list = self.scanNewSchImages(image_paths, sch_type)
        new_count = []
        for sch in sch_list: new_count.append(self.getTypeCounts(sch, sch_type))
        new_image_paths = self.reconstructSchImage(sch_list, files, sch_type)

        return [original_count, new_count], [image_paths, new_image_paths]