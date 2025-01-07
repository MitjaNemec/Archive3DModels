import os
import os.path
import logging
import shutil
import sys
import re
import argparse
import pcbnew
logger = logging.getLogger(__name__)


def get_variable(env_var):
    path = os.getenv(env_var)

    if path is None and (env_var == "KISYS3DMOD" or re.match("KICAD.*_3DMODEL_DIR", env_var)):
        path = os.getenv("KICAD7_3DMODEL_DIR")

        if path is None:
            path = os.getenv("KICAD6_3DMODEL_DIR")
        
    return path


class Archiver():
    def __init__(self, model_local_path="packages3D"):
        self.model_local_path = model_local_path

    def archive_3d_models(self, board, remap_missing_models=False, out_prj_path=None):
        logger.info("Starting to archive 3D models")

        logger.debug("All defined environment variables: " + repr(os.environ))

        # prepare folder for 3D models
        prj_path = os.path.dirname(os.path.abspath(board.GetFileName()))

        if out_prj_path is None:
            out_prj_path = prj_path

        model_folder_path = os.path.normpath(os.path.join(out_prj_path, self.model_local_path))

        # go to project folder
        os.chdir(prj_path)

        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        # get all footprints
        footprints = board.GetFootprints()

        # go through all footprints
        not_copied = []
        for fp in footprints:
            fp_ref = fp.GetReference()
            logger.debug("Getting 3D models for footprint of: " + fp_ref)
            # find all 3D models linked to footprint
            models = fp.Models()
            # go through all models bound to footprint
            # bad python API
            nr_models = len(models)
            models_to_push_back = []
            for index in range(nr_models):
                # pop one 3D model from the list
                model = models.pop()
                # copy 3D model
                model_path = model.m_Filename
                logger.debug("Trying to copy: " + model_path)

                # check if model path includes environment variable
                abs_model_path = None
                if "${" in model_path:
                    start_index = model_path.find("${")+2
                    end_index = model_path.find("}")
                    env_var = model_path[start_index:end_index]

                    path = get_variable(env_var)
                    # if variable is defined, find proper model path
                    if path is not None:
                        abs_model_path = os.path.normpath(path+model_path[end_index+1:])
                    # if variable is not defined, we can not find the model. Thus don't put it on the list
                    else:
                        logger.info("Can not find model defined with enviroment variable:\n" + model_path)
                        abs_model_path = None
                elif "$(" in model_path:
                    start_index = model_path.find("$(")+2
                    end_index = model_path.find(")")
                    env_var = model_path[start_index:end_index]

                    path = get_variable(env_var)
                    # if variable is defined, find proper model path
                    if path is not None:
                        abs_model_path = os.path.normpath(path+model_path[end_index+1:])
                    # if variable is not defined, we can not find the model. Thus don't put it on the list
                    else:
                        logger.info("Can not find model defined with enviroment variable:\n" + model_path)
                        abs_model_path = None
                # check if there is no path (model is local to project)
                elif prj_path == os.path.dirname(os.path.abspath(model_path)):
                    abs_model_path = os.path.abspath(model_path)
                # check if model is given with absolute path
                elif os.path.exists(model_path):
                    abs_model_path = os.path.abspath(model_path)
                # otherwise we don't know how to parse the path
                else:
                    logger.info("Ambiguous path for the model: " + model_path)
                    # test default 3D_library location if defined
                    if os.getenv("KICAD6_3DMODEL_DIR"):
                        if os.path.exists(os.path.normpath(os.path.join(os.getenv("KICAD6_3DMODEL_DIR"), model_path))):
                            abs_model_path = os.path.normpath(os.path.join(os.getenv("KICAD6_3DMODEL_DIR"), model_path))
                            logger.info("Going with: " + abs_model_path)
                    # test default 3D_library location if defined
                    elif os.getenv("KICAD7_3DMODEL_DIR"):
                        if os.path.exists(os.path.normpath(os.path.join(os.getenv("KICAD7_3DMODEL_DIR"), model_path))):
                            abs_model_path = os.path.normpath(os.path.join(os.getenv("KICAD7_3DMODEL_DIR"), model_path))
                            logger.info("Going with: " + abs_model_path)
                    # testing project folder location
                    elif os.path.exists(os.path.normpath(os.path.join(prj_path, model_path))):
                        abs_model_path = os.path.normpath(os.path.join(prj_path, model_path))
                        logger.info("Going with: " + abs_model_path)
                    else:
                        abs_model_path = None
                        logger.info("Can not find model defined with: " + model_path)

                # copy model
                model_missing = True
                if abs_model_path:
                    model_without_extension = abs_model_path.rsplit('.', 1)[0]
                    for ext in ['.wrl', '.stp', '.step', '.igs', '.WRL', '.STP', '.STEP', '.IGS']:
                        try:
                            shutil.copy2(model_without_extension + ext, model_folder_path)
                            model_missing = False
                        # src and dst are the same
                        except shutil.Error:
                            model_missing = False
                        # file not found
                        except (OSError, IOError):
                            pass
                # correct abs_model path for logging
                else:
                    abs_model_path = model_path

                if model_missing:
                    logger.debug("Did not copy: " + model.m_Filename)
                    not_copied.append((fp_ref, model.m_Filename))

                if not model_missing or remap_missing_models:
                    logger.debug("Remapping: " + model.m_Filename)
                    filename = os.path.basename(abs_model_path)
                    new_path = "${KIPRJMOD}" + "/" + self.model_local_path + "/" + filename
                    model.m_Filename = new_path

                # and push it to the back of the list (changed or unchaged)
                models_to_push_back.append(model)
            # push all the models back
            for m in models_to_push_back:
                models.push_back(m)

        if not_copied:
            not_copied_pretty = [(x[0], os.path.normpath(x[1])) for x in not_copied]
            str_list = [repr(x) for x in not_copied_pretty]
            logger.warning("Did not succeed to copy 3D models:\n"
                        + "\n".join(str_list))
            return not_copied
        else:
            return []

class Archive3DModelsCLI:
    def __init__(self, args):
        # plugin paths
        self.plugin_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.version_file_path = os.path.join(self.plugin_folder, 'version.txt')

        # read version
        with open(self.version_file_path) as fp:
            self.version = fp.readline()

    def Run(self, args):
        # load board
        board = pcbnew.LoadBoard(args.pcb_file)

        # go to the project folder - so that log will be in proper place
        os.chdir(args.project_dir)

        # set up logger
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            # handlers=handlers
                            )
        logger = logging.getLogger(__name__)
        logger.info("Plugin executed on: " + repr(sys.platform))
        logger.info("Plugin executed with python version: " + repr(sys.version))
        logger.info("KiCad build version: " + str(pcbnew.GetBuildVersion()))
        logger.info("Plugin version: " + self.version)

        if args.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # wrap the call, to catch and log any exceptions
        try:
            archiver = Archiver(args.model_local_path)
            # and run the plugin
            archiver.archive_3d_models(board, remap_missing_models=args.disallow_missing_models, out_prj_path=args.out_dir)

            pcbnew.SaveBoard(os.path.join(args.out_dir, os.path.basename(args.pcb_file)), board)
        except Exception:
            logger.exception("Fatal error when creating an instance of Archive 3D models")
            # e_dlg = ErrorDialog(self.frame)
            # e_dlg.ShowModal()
            # e_dlg.Destroy()

        # clean up before exiting
        # main_dlg.Destroy()
        logging.shutdown()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='KiCad Archive 3D Models plugin CLI.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('pcb_file', help="KiCad PCB file")
    parser.add_argument('out_dir', help="Save resulting PCB and models to specified path. Uses directory of the PCB file by default")
    parser.add_argument('--model-local-path', default="packages3D", help="Directory to copy 3D models to")
    parser.add_argument('--project-dir', help="Project directory to use as KIPRJMOD. Uses directory of the PCB file by default")
    parser.add_argument('--library-3dmodel', default=None, help="Path where the 3D models are installed in (KICAD*_3DMODEL_DIR)")
    parser.add_argument('--debug', default=False, action="store_true", help="Enable debug logging")
    parser.add_argument('--disallow-missing-models', default=False, action="store_true", help="Disallow missing models")

    args = parser.parse_args()

    if args.project_dir is None:
        args.project_dir = os.path.dirname(os.path.abspath(args.pcb_file))

    os.environ['KIPRJMOD'] = args.project_dir

    if args.library_3dmodel is not None:
        os.environ['KICAD8_3DMODEL_DIR'] = args.library_3dmodel

    Archive3DModelsCLI(args).Run(args)