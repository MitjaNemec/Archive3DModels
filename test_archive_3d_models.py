import unittest
from archive_3d_models import Archiver
import pcbnew
import logging
import sys
import os

# read the configuration from a file
from configparser import ConfigParser
parser = ConfigParser()
parser.read('config.ini')
model_local_path = parser.get('config', 'model_local_path')
if parser.get('config', 'allow_missing_models') == 'True':
    amm = True
else:
    amm = False
debug_level = parser.get('debug', 'debug_level')

# mock environment variables
#os.environ["KICAD6_3DMODEL_DIR"] = "/home/mitjan/Documents/Plate/Kicad_libs/official_libs/kicad-packages3D_V6/"
os.environ["KICAD7_3DMODEL_DIR"] = "/home/mitjan/Documents/Plate/Kicad_libs/official_libs/kicad-packages3D_V7/"


class TestArchive3DModels(unittest.TestCase):
    def test_fresh_remap_missing(self):
        os.chdir('Fresh_test_project')

        import compare_boards
        os.environ["KIPRJMOD"] = os.path.abspath(os.getcwd())
        in_filename = 'Fresh_test_project.kicad_pcb'
        out_filename = 'Fresh_test_project_temp.kicad_pcb'
        ref_filename = 'Fresh_test_project_reference_allow.kicad_pcb'
        board = pcbnew.LoadBoard(in_filename)
        archiver = Archiver(model_local_path)

        not_copied_list = archiver.archive_3d_models(board, remap_missing_models=True)

        self.assertEqual(len(not_copied_list), 2, "Should be 2")

        saved = pcbnew.SaveBoard(out_filename, board)
        nr_errors = compare_boards.compare_boards(out_filename, ref_filename)
        self.assertEqual(nr_errors, 0, "Should be 0")
        # check if files are present
        files = ["C_0805_2012Metric", "C_1206_3216Metric",
                 "PinHeader_1x02_P2.00mm_Vertical", "PinHeader_1x02_P2.54mm_Vertical",
                 "R_1206_3216Metric"]
        for f in files:
            model_dir = os.path.normpath(os.getcwd() + model_local_path)
            filepath = os.path.join(model_dir, f)
            found_at_least_one = False
            for ext in ['.wrl', '.stp', '.step', '.igs']:
                filename = filepath + ext
                if os.path.exists(filename):
                    found_at_least_one = True
                    os.remove(filepath + ext)
            self.assertTrue(found_at_least_one, filepath)
        os.remove(out_filename)
        os.rmdir(model_dir)
        os.chdir("..")

    def test_fresh_dont_remap_missing(self):
        os.chdir('Fresh_test_project')

        import compare_boards
        os.environ["KIPRJMOD"] = os.path.abspath(os.getcwd())
        in_filename = 'Fresh_test_project.kicad_pcb'
        out_filename = 'Fresh_test_project_temp.kicad_pcb'
        ref_filename = 'Fresh_test_project_reference_dont_allow.kicad_pcb'
        board = pcbnew.LoadBoard(in_filename)
        archiver = Archiver(model_local_path)

        not_copied_list = archiver.archive_3d_models(board, remap_missing_models=False)

        self.assertEqual(len(not_copied_list), 2, "Should be 2")

        saved = pcbnew.SaveBoard(out_filename, board)
        nr_errors = compare_boards.compare_boards(out_filename, ref_filename)
        self.assertEqual(nr_errors, 0, "Should be 0")
        # check if files are present
        files = ["C_0805_2012Metric", "C_1206_3216Metric",
                 "PinHeader_1x02_P2.00mm_Vertical", "PinHeader_1x02_P2.54mm_Vertical",
                 "R_1206_3216Metric"]
        for f in files:
            model_dir = os.path.normpath(os.getcwd() + model_local_path)
            filepath = os.path.join(model_dir, f)
            found_at_least_one = False
            for ext in ['.wrl', '.stp', '.step', '.igs']:
                filename = filepath + ext
                if os.path.exists(filename):
                    found_at_least_one = True
                    os.remove(filepath + ext)
            self.assertTrue(found_at_least_one, filepath)
        os.remove(out_filename)
        os.rmdir(model_dir)
        os.chdir("..")


if __name__ == '__main__':
    file_handler = logging.FileHandler(filename='archive_3d_models.log', mode='w')
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging_level = logging.INFO
    if debug_level.lower() == 'debug':
        logging_level = logging.DEBUG
    if debug_level.lower() == 'info':
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level,
                        format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        handlers=handlers
                        )

    logger = logging.getLogger(__name__)
    logger.info("Plugin executed on: " + repr(sys.platform))
    logger.info("Plugin executed with python version: " + repr(sys.version))
    logger.info("KiCad build version: " + str(pcbnew.GetBuildVersion()))

    unittest.main()
