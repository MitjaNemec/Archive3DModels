try:
    # Note the relative import!
    from .action_archive_3d_models import Archive3DModels
    # Instantiate and register to Pcbnew
    Archive3DModels().register()
# if failed, log the error and let the user know
except Exception as e:
    # log the error
    import os
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    log_file = os.path.join(plugin_dir, 'archive_3d_models_error.log')
    with open(log_file, 'w') as f:
        f.write(repr(e))
    # register dummy plugin, to let the user know of the problems
    import pcbnew
    import wx

    class Archive3DModels(pcbnew.ActionPlugin):
        """
        Notify user of missing wxpython
        """

        def defaults(self):
            self.name = "Archive 3DModels"
            self.category = "Get compound PCB data"
            self.description = "Dummy plugin for minimal user feedback"

        def Run(self):
            caption = self.name
            message = "There was an error while loading plugin \n" \
                      "Please take a look in the plugin folder for archive_3d_models_error.log\n" \
                      "You can raise an issue on GitHub page.\n" \
                      "Please attach the .log file"
            dlg = wx.MessageBox(message, caption, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    Archive3DModels().register()

