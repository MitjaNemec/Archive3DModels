#! /bin/bash

# refresh derived resources
inkscape --without-gui archive_3d_models_dark.svg -w 24 -h 24 -o archive_3d_models_dark.png
inkscape --without-gui archive_3d_models_light.svg -w 24 -h 24 -o archive_3d_models_light.png
inkscape --without-gui archive_3d_models_light.svg -w 64 -h 64 -o archive_3d_models.png

# grab version and parse it into metadata.json
version=`cat version.txt`
sed -i -e "s/VERSION/$version/g" metadata.json

# prepare the package
mkdir plugins
cp config.ini plugin
cp archive_3d_models_dark.png plugin
cp archive_3d_models_light.png plugin
cp __init__.py plugin
cp action_archive_3d_models.py plugin
cp archive_3d_models_end_GUI.py plugin
cp archive_3d_models_main_GUI.py plugin
cp archive_3d_models_settings_GUI.py plugin
cp archive_3d_models.py plugin
cp version.txt plugin
mkdir resources
cp archive_3d_models.jpg resources/icon.png

zip -r Archive3DModels-$version-pcm.zip plugins resources metadata.json

# clean up
rm -r resources
rm -r plugins