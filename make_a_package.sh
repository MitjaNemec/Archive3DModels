#! /bin/bash

# refresh derived resources
inkscape archive_3d_models_dark.svg -w 24 -h 24 -o archive_3d_models_dark.png
inkscape archive_3d_models_light.svg -w 24 -h 24 -o archive_3d_models_light.png
inkscape archive_3d_models_light.svg -w 64 -h 64 -o archive_3d_models.png

# refresh the GUI design
wxformbuilder -g Archive3DModels_end_GUI.fbp
wxformbuilder -g Archive3DModels_main_GUI.fbp
wxformbuilder -g Archive3DModels_settings_GUI.fbp
wxformbuilder -g error_dialog_GUI.fbp

# grab version and parse it into metadata.json
cp metadata_source.json metadata_package.json
version=`cat version.txt`
# remove all but the latest version in package metadata
python3 parse_metadata_json.py
sed -i -e "s/VERSION/$version/g" metadata.json

# cut the download, sha and size fields
sed -i '/download_url/d' metadata.json
sed -i '/download_size/d' metadata.json
sed -i '/install_size/d' metadata.json
sed -i '/download_sha256/d' metadata.json

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
cp error_dialog_GUI.py plugins
cp archive_3d_models.py plugins
cp version.txt plugins
mkdir resources
cp archive_3d_models.png resources/icon.png

zip -r Archive3DModels-$version-pcm.zip plugins resources metadata.json

# clean up
rm -r resources
rm -r plugins
rm metadata.json

# get the sha, size and fill them in the metadata
cp metadata_source.json metadata.json
version=`cat version.txt`
sed -i -e "s/VERSION/$version/g" metadata.json
zipsha=`sha256sum Archive3DModels-$version-pcm.zip | xargs | cut -d' ' -f1`
sed -i -e "s/SHA256/$zipsha/g" metadata.json
unzipsize=`unzip -l Archive3DModels-$version-pcm.zip | tail -1 | xargs | cut -d' ' -f1`
sed -i -e "s/INSTALL_SIZE/$unzipsize/g" metadata.json
dlsize=`ls -al Archive3DModels-$version-pcm.zip | tail -1 | xargs | cut -d' ' -f5`
sed -i -e "s/DOWNLOAD_SIZE/$dlsize/g" metadata.json
