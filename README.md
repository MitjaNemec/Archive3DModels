# Archive 3D models

This plugin copies footprint 3D models to the project local subfolder (default name: packages3D). The plugin also updates the links to the models within the layout (.kicad_pcb) file so that they point to the archived 3D models with a path relative to the project folder.

If the footprint is updated, the 3Dmodel path is also updated. Thus the plugin should be re-run.

# Command-line interface

This plugin can be invoked from command line. It can also save the project into another specified directory instead of overwriting.

Typical Batch script:

```batch
@echo off
pushd .
call "C:\Program Files\KiCad\8.0\bin\kicad-cmd.bat"
popd

python "%USERPROFILE%\Documents\kicad\8.0\3rdparty\plugins\com_github_MitjaNemec_Archive3DModels\archive_3d_models.py" --library-3dmodel "C:/Program Files/KiCad/8.0/share/kicad/3dmodels/" <your_pcb>.kicad_pcb <your_pcb>_Project3D
```