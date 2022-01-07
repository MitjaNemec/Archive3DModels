#! /bin/bash

# refresh derived resources
inkscape archive_3d_models_dark.svg -w 24 -h 24 -o archive_3d_models_dark.png
inkscape archive_3d_models_light.svg -w 24 -h 24 -o archive_3d_models_light.png
inkscape archive_3d_models_light.svg -w 64 -h 64 -o archive_3d_models.png

# refresh the GUI design
~/WxFormBuilder/bin/wxformbuilder -g Archive3DModels_end_GUI.fbp
~/WxFormBuilder/bin/wxformbuilder -g Archive3DModels_main_GUI.fbp
~/WxFormBuilder/bin/wxformbuilder -g Archive3DModels_settings_GUI.fbp

# grab version and parse it into metadata.json
cp metadata_source.json metadata.json
version=`cat version.txt`
sed -i -e "s/VERSION/$version/g" metadata.json

# prepare the package
mkdir plugins
cp config.ini plugins
cp archive_3d_models_dark.png plugins
cp archive_3d_models_light.png plugins
cp __init__.py plugins
cp action_archive_3d_models.py plugins
cp archive_3d_models_end_GUI.py plugins
cp archive_3d_models_main_GUI.py plugins
cp archive_3d_models_settings_GUI.py plugins
cp archive_3d_models.py plugins
cp version.txt plugins
mkdir resources
cp archive_3d_models.png resources/icon.png

zip -r Archive3DModels-$version-pcm.zip plugins resources metadata.json

# clean up
rm -r resources
rm -r plugins
