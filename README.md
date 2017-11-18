# 150-Cloud-Apps
A *cloud application* to connect individuals, blood banks, and hospitals.

## Running Locally
The project relies on Google Cloud SDK and its Python extension. Installatin instructions can be found [here](https://cloud.google.com/appengine/docs/standard/python/download). Make sure that the Python libraries can be imported by the Python interpreter. I had to add the symbolic link from `/usr/lib/python2.7/google -> /usr/lib/google-cloud-sdk/platform/google_appengine/google/` on Ubuntu to get this working.

Once done, the app can be started with `dev_appserver.py app.yaml`. It sets Flask debugging when run locally although Google does not play nicely with this. 

## Deploying
`appengine_config.py` tells the Google App Engine to look in the folder `/lib/` for vendor libraries. The production runtime includes some [third party libraries](https://cloud.google.com/appengine/docs/standard/python/tools/built-in-libraries-27) but any others should be included in this folder before uploading the project. These libraries are kept up to date in the `requirements.txt` file.

To populare or update the libraries directory, run `pip install -t lib -r requirements.txt` from a virtual environment.
