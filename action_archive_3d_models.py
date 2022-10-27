# -*- coding: utf-8 -*-
#  action_archive_3d_models.py
#
# Copyright (C) 2022 Mitja Nemec
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import wx
import pcbnew
import os
import logging
import sys
from configparser import ConfigParser
from .archive_3d_models import Archiver
from .archive_3d_models_main_GUI import Archive3DModelsMainGui
from .archive_3d_models_settings_GUI import Archive3DModelsSettingsGui
from .archive_3d_models_end_GUI import Archive3DModelsEndGui
from .error_dialog_GUI import ErrorDialogGUI


class ErrorDialog(ErrorDialogGUI):
    def SetSizeHints(self, sz1, sz2):
        # DO NOTHING
        pass

    def __init__(self, parent):
        super(ErrorDialog, self).__init__(parent)


class EndReport(Archive3DModelsEndGui):
    def SetSizeHints(self, sz1, sz2):
        # DO NOTHING
        pass

    def __init__(self, parent, list_of_models):
        super(EndReport, self).__init__(parent)
        # fill the TextCtrl
        str_list = [str(x[0])+": "+str(x[1]) for x in list_of_models]
        self.txt_list.Value = "\n".join(str_list)

    def on_copy(self, event):
        data = wx.TextDataObject()
        data.SetText(self.txt_list.GetValue())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")


class MainWindow(Archive3DModelsMainGui):
    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        # DO NOTHING
        pass

    def __init__(self, parent, config_file_path):
        super(MainWindow, self).__init__(parent)
        self.config_file_path = config_file_path

    def on_run(self, event):
        self.EndModal(True)

    def on_close(self, event):
        self.EndModal(False)

    def on_settings(self, event):
        sett_dlg = SettingsWindow(self, self.config_file_path)
        sett_dlg.ShowModal()
        sett_dlg.Destroy()


class SettingsWindow(Archive3DModelsSettingsGui):
    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        # DO NOTHING
        pass

    def __init__(self, parent, config_file_path):
        super(SettingsWindow, self).__init__(parent)
        self.config_file_path = config_file_path
        # load config if it exists
        if os.path.exists(self.config_file_path):
            # read the file
            parser = ConfigParser()
            parser.read(self.config_file_path)
            # parse the data structure
            model_local_path = parser.get('config', 'model_local_path')
            if parser.get('config', 'allow_missing_models') == 'True':
                amm = True
            else:
                amm = False
            debug_level = parser.get('debug', 'debug_level')
        else:
            # set defaults
            amm = True
            debug_level = 'info'
            model_local_path = '/packages3D'
            # prep the data structure
            parser = ConfigParser()
            parser.read('config.ini')
            parser.set('config', 'model_local_path', model_local_path)
            parser.set('config', 'allow_missing_models', amm)
            parser.set('debug', 'debug_level', debug_level)
            # write the file
            with open(self.config_file_path, 'w') as configfile:
                parser.write(configfile)
        # set the GUI elements
        self.cb_amm.SetValue(amm)
        self.txt_path.SetValue(model_local_path)
        self.cb_debug_level.SetValue(debug_level)

    def on_ok(self, event):
        # read the values
        amm = str(self.cb_amm.GetValue())
        model_local_path = self.txt_path.GetLineText(0)
        debug_level = self.cb_debug_level.GetStringSelection()
        # prep the data structure
        parser = ConfigParser()
        parser.read(self.config_file_path)
        parser.set('config', 'model_local_path', model_local_path)
        parser.set('config', 'allow_missing_models', amm)
        parser.set('debug', 'debug_level', debug_level)
        # write the file
        with open(self.config_file_path, 'w') as configfile:
            parser.write(configfile)

        # exit dialog
        self.EndModal(wx.ID_OK)

    def on_close(self, event):

        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):

        self.EndModal(wx.ID_OK)


class Archive3DModels(pcbnew.ActionPlugin):
    """
    A plugin to show copy and remap footprint 3D models into project local subfolder
    How to use:
    - run the plugin
    """
    def __init__(self):
        super(Archive3DModels, self).__init__()

        self.frame = None

        self.name = "Archive 3D models"
        self.category = "Archive"
        self.description = "Copy and remap footprint 3D models into project local subfolder"
        self.icon_file_name = os.path.join(
                os.path.dirname(__file__), 'archive_3d_models_light.png')
        self.dark_icon_file_name = os.path.join(
                os.path.dirname(__file__), 'archive_3d_models_dark.png')
        # read the configuration
        # plugin paths
        self.plugin_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.config_file_path = os.path.join(self.plugin_folder, 'config.ini')
        self.version_file_path = os.path.join(self.plugin_folder, 'version.txt')

        # read config
        parser = ConfigParser()
        parser.read(self.config_file_path)
        self.model_local_path = parser.get('config', 'model_local_path')
        if parser.get('config', 'allow_missing_models') == 'True':
            self.amm = True
        else:
            self.amm = False
        self.debug_level = parser.get('debug', 'debug_level')

        # read version
        with open(self.version_file_path) as fp:
            self.version = fp.readline()

    def defaults(self):
        pass

    def Run(self):
        # grab pcbeditor frame
        self.frame = wx.FindWindowByName("PcbFrame")

        # load board
        board = pcbnew.GetBoard()

        # go to the project folder - so that log will be in proper place
        os.chdir(os.path.dirname(os.path.abspath(board.GetFileName())))

        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        file_handler = logging.FileHandler(filename='archive_3d_models.log', mode='w')
        handlers = [file_handler]

        # set up logger
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            handlers=handlers)
        logger = logging.getLogger(__name__)
        logger.info("Plugin executed on: " + repr(sys.platform))
        logger.info("Plugin executed with python version: " + repr(sys.version))
        logger.info("KiCad build version: " + str(pcbnew.GetBuildVersion()))
        logger.info("Plugin version: " + self.version)

        # GUI DPI scaling issue logging details
        displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
        sizes = [display.GetGeometry().GetSize() for display in displays]
        logger.info("Screen sizes: " + repr(sizes))

        # open dialog
        main_dlg = MainWindow(self.frame, self.config_file_path)
        main_dlg.CenterOnParent()

        dlg_size = main_dlg.GetSize()
        logger.info("Dialog size: " + repr(dlg_size))

        logger.info("Char size: " + repr(dlg_size.GetCharHeight()))

        # run the plugin
        if main_dlg.ShowModal():
            # read the config
            try:
                parser = ConfigParser()
            except Exception:
                logger.exception("Fatal error when creating an instance of Archie 3D models")
                e_dlg = ErrorDialog(self.frame)
                e_dlg.ShowModal()
                e_dlg.Destroy()
                logging.shutdown()
                return
            parser.read(self.config_file_path)
            model_local_path = parser.get('config', 'model_local_path')
            if parser.get('config', 'allow_missing_models') == 'True':
                amm = True
            else:
                amm = False
            debug_level = parser.get('debug', 'debug_level')
            logging_level = logging.INFO
            if debug_level.lower() == 'debug':
                logging_level = logging.DEBUG
            if debug_level.lower() == 'info':
                logging_level = logging.INFO
            logger.setLevel(logging_level)

            # wrap the call, to catch and log any exceptions
            try:
                archiver = Archiver(model_local_path)
                # and run the plugin
                not_copied_list = archiver.archive_3d_models(board, remap_missing_models=amm)
                # when finished, let the user know which models are missing
                e_dlg = EndReport(self.frame, not_copied_list)
                e_dlg.ShowModal()
                e_dlg.Destroy()
                pcbnew.Refresh()
            except Exception:
                logger.exception("Fatal error when creating an instance of Archie 3D models")
                e_dlg = ErrorDialog(self.frame)
                e_dlg.ShowModal()
                e_dlg.Destroy()

        # clean up before exiting
        main_dlg.Destroy()
        logging.shutdown()
