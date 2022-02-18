import os
import os.path
import logging
import shutil
logger = logging.getLogger(__name__)


class Archiver():
    def __init__(self, model_local_path="/packages3D"):
        self.model_local_path = model_local_path

    def archive_3d_models(self, board, remap_missing_models=False):
        logger.info("Starting to archive 3D models")

        logger.debug("All defined environment variables: " + repr(os.environ))

        # prepare folder for 3D models
        prj_path = os.path.dirname(os.path.abspath(board.GetFileName()))
        model_folder_path = os.path.normpath(prj_path + self.model_local_path)

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
            logger.info("Getting 3D models for footprint of: " + fp_ref)
            # find all 3D models linked to footprint
            models = fp.Models()
            # go through all models bound to footprint
            # bad python API
            nr_models = range(len(models))
            for index in nr_models:
                # pop one 3D model from the list
                model = models.pop()
                # copy 3D model
                model_path = model.m_Filename
                logger.info("Trying to copy: " + model_path)

                if "${" in model_path:
                    start_index = model_path.find("${")+2
                    end_index = model_path.find("}")
                    env_var = model_path[start_index:end_index]

                    path = os.getenv(env_var)

                    # if variable is defined, find proper model path
                    if path is not None:
                        abs_model_path = os.path.normpath(path+model_path[end_index+1:])
                    # if variable is not defined, we can not find the model. Thus don't put it on the list
                    else:
                        logger.info("Can not find model defined with enviroment variable:\n" + model_path)
                        abs_model_path = None
                # check if there is no path (model is local to project
                elif prj_path == os.path.dirname(os.path.abspath(model_path)):
                    abs_model_path = os.path.abspath(model_path)
                # check if model is given with absolute path
                elif os.path.exists(model_path):
                    abs_model_path = os.path.abspath(model_path)
                # otherwise we don't know how to parse the path
                else:
                    logger.info("Ambiguous path for the model: " + model_path)
                    # test default 3D_library location "KICAD6_3DMODEL_DIR"
                    if os.path.exists(os.path.normpath(os.path.join(os.getenv("KICAD6_3DMODEL_DIR"),model_path))):
                        # testing project folder location
                        abs_model_path = os.path.normpath(os.path.join(os.getenv("KICAD6_3DMODEL_DIR"),model_path))
                        logger.info("Going with: " + abs_model_path)
                    elif os.path.exists(os.path.normpath(os.path.join(prj_path, model_path))):
                        abs_model_path = os.path.normpath(os.path.join(prj_path, model_path))
                        logger.info("Going with: " + abs_model_path)
                    else:
                        logger.info("Can not find model defined with: " + model_path)
                        abs_model_path = None

                # copy model
                model_missing = True
                if abs_model_path:
                    model_without_extension = abs_model_path.rsplit('.', 1)[0]
                    for ext in ['.wrl', '.stp', '.step', '.igs']:
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
                    logger.info("Did not copy: " + model.m_Filename)
                    not_copied.append((fp_ref, model.m_Filename))

                if not model_missing or remap_missing_models:
                    logger.info("Remapping: " + model.m_Filename)
                    filename = os.path.basename(abs_model_path)
                    new_path = "${KIPRJMOD}" + self.model_local_path + "/" + filename
                    model.m_Filename = new_path

                # and push it to the back of the list (changed or unchaged)
                models.push_back(model)

        if not_copied:
            not_copied_pretty = [(x[0], os.path.normpath(x[1])) for x in not_copied]
            str_list = [repr(x) for x in not_copied_pretty]
            logger.info("Did not succeed to copy 3D models!\n"
                        + "\n".join(str_list))
            return not_copied
        else:
            return []
