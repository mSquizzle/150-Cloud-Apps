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
- [Set up a Cloud SQL MySQL database](https://cloud.google.com/sql/docs/mysql/quickstart#create_a_title_short_instance)
  1. Create second generation Cloud SQL instance within the same GAE project
  1. Set a `root` password for the instance
- [Authorize your client machine](https://cloud.google.com/sql/docs/mysql/sql-proxy#gcloud)
  1. Go through the `gcloud init` proces if you haven't already and choose your project
  1. Authorize client machine with `gcloud auth-default login` in order to allow the proxy to use your credentials for authentication 
  1. Go ahead and run `gcloud auth login` for good measure
- Setup the [Cloud SQL proxy binary](https://cloud.google.com/sql/docs/mysql/sql-proxy)
  1. Download the [binary](https://cloud.google.com/sql/docs/mysql/sql-proxy#install)
  1. Make it executable with `chmod +x cloud_sql_proxy`
  1. For long-term it makes sense to move the binary to a directory like `/usr/local/bin`
- Set environment variable for the Cloud SQL root password
  1. Set`CLOUDSQL_PASSWORD` to your Cloud SQL root password in `app.yaml` by adding a [directive](https://cloud.google.com/appengine/docs/flexible/python/configuring-your-app-with-app-yaml#Python_app_yaml_Defining_environment_variables)
  ```
  env_variables:
    CLOUDSQL_PASSWORD: 'my_root_pass'
  ```

### Development Server
Once the libraries and database proxy are setup the application can be started with `dev_appserver.py app.yaml`. Flask debugging is set when run locally although Google does not play nicely with this. 

## Deploying
`appengine_config.py` tells the Google App Engine to look in the folder `lib/` for vendor libraries. The production runtime includes some [third party libraries](https://cloud.google.com/appengine/docs/standard/python/tools/built-in-libraries-27) but any others should be installed to this directory before deploying the project with the command `pip install -t lib -r requirements.txt`.

Deploy the application with `gcloud app deploy`.
