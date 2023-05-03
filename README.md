# To install
`brew install GDAL` \
Create a Python venv and install packages.\
`python -m venv venv/` \
`python -m pip install numpy` \
`python -m pip install -r requirements.txt`

Make aws account
aws CLI


Download satellite data from AWS \
`aws s3 cp s3://spacenet-dataset/spacenet/SN3_roads/tarballs/SN3_roads_train_AOI_3_Paris_geojson_roads_speed.tar.gz .` \
`aws s3 cp s3://spacenet-dataset/spacenet/SN3_roads/tarballs/SN3_roads_train_AOI_3_Paris.tar.gz .` \
`aws s3 cp s3://spacenet-dataset/spacenet/SN2_buildings/tarballs/SN2_buildings_train_AOI_3_Paris.tar.gz .`

Expand \
`tar -xf SN3_roads_train_AOI_3_Paris_geojson_roads_speed.tar.gz` \
`tar -xf SN3_roads_train_AOI_3_Paris.tar.gz` \
`tar -xf SN2_buildings_train_AOI_3_Paris.tar.gz`



download data from https://spacenet.ai/paris/

