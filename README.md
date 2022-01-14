# Archive 3D models

This plugin copies footprint 3D models to the project local subfolder (default name: packages3D). The plugin also updates the links to the models within the layout (.kicad_pcb) file so that they point to the archived 3D models with a path relative to the project folder.

If the footprint is updated, the 3Dmodel path is also updated. Thus the plugin should be re-run.