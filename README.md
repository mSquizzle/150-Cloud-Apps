# 150-Cloud-Apps
A *cloud application* to connect individuals, blood banks, and hospitals.

## Running Locally
### Libraries
The project relies on Google Cloud SDK and its Python extension. Installation instructions can be found [here](https://cloud.google.com/appengine/docs/standard/python/download). Make sure that the Python libraries can be imported by the Python interpreter; I had to add the symbolic link `/usr/lib/python2.7/google -> /usr/lib/google-cloud-sdk/platform/google_appengine/google/` on Ubuntu to get this working.

Necessary 3rd party libraries are kept up to date in the `requirements.txt` file. There are three options to handle these requirements for local development:
- Install on your system normally with `sudo pip install -r requirements.txt`
- Install within a virtual environment
- Install to the `lib` directory with `pip install -t lib -r requirements.txt`

The last option is required when pushing the application to Google App Engine. See the [Deploying](#deploying) section for an explanation.

### Windows Import Issues
Note that for Windows users, you may run into issues related to Flask. If you are running into problems because you cannot import `msvcrt`, you can go into `appengine_config.py` and add the following after `from google.appengine.ext import vendor`:

```import os
 import sys

 if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
   sys.path.insert(0, 'lib')
 else:
   if os.name == 'nt':
     os.name = None
```

### Database Proxy
- [Basic project setup](https://cloud.google.com/sql/docs/mysql/quickstart#before-you-begin)
  1. Create GAE Project
  1. Enable billing
  1. Enable CloudSQL API
- Set up a Cloud SQL MySQL database
  1. Create second generation Cloud SQL instance within the same GAE project
  1. Set a `root` password for the instance
- Authorize your client machine
  1. Go through the `gcloud init` proces if you haven't already and choose your project
  1. Authorize client machine with `gcloud atuh login`
  1. This is undocumented but in order to fully authorize for Cloud SQL, run `gcloud auth application-default` :thumbsdown:
- Download the [Cloud SQL proxy binary](https://cloud.google.com/sql/docs/mysql/sql-proxy)
- Set the `CLOUDSQL_PASSWORD` as an environment variable so that the application can connect

### Development Server
Once the libraries and database proxy are setup the application can be started with `dev_appserver.py app.yaml`. Flask debugging is set when run locally although Google does not play nicely with this. 

## Deploying
`appengine_config.py` tells the Google App Engine to look in the folder `lib/` for vendor libraries. The production runtime includes some [third party libraries](https://cloud.google.com/appengine/docs/standard/python/tools/built-in-libraries-27) but any others should be installed to this directory before deploying the project with the command `pip install -t lib -r requirements.txt`.

Deploy the application with `gcloud app deploy`.
