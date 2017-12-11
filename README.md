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
  1. Create Google App Engine Project
  1. Enable billing
  1. Enable Cloud SQL API
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
- Set appropriate [environment variables](https://cloud.google.com/appengine/docs/flexible/python/configuring-your-app-with-app-yaml#Python_app_yaml_Defining_environment_variables) in `app.yaml`
  - `CLOUDSQL_PASSWORD` is the root password for your MySQL instance
  - `CLOUDSQL_CONNECTION_NAME` is the Cloud SQL connection in the format `<PROJECT_ID>:<REGION>:<INSTANCE_ID>`
  - `PROJECT_ID` is the project; should be the same as the first part of the `CLOUDSQL_CONNECTION_NAME`
- Define the SQL tables once the proxy is running
  - If you have a MySQL client installed run `sql/setup.sh` to connect to the proxy, and create the database and tables 
  - Otherwise, log into the Cloud SQL console and run the `sql/mrs.sql` commands manualy
  
For the last step, you need to be running the Cloud SQL proxy. This can be done by running: `cloud_sql_proxy -instances=<PROJECT_ID>:<REGION>:<INSTANCE_ID>=tcp:3306` (although the `cloud_sql_proxy` program may have to be invoked differently depending on how you installed it)

### API Keys
- In order to the Map embed and the Autocomplete box to work for events, you will need to have a valid Google Maps Key.
  1. In the application console under APIs, enable the Google Map Javascript and Google Map Embed APIs for your application.
  2. Generate an API key under credentials. For production you may want to limit the how this key is used, but for local development, no restrictions should be needed.
  3. In app.yaml, set the MAPS_KEY environment variable to the newly generated API key.
- The RTE in the email admin is powered by [TinyMCE](https://www.tinymce.com/). You will need to obtain a key in order to use it.
  1. Login to TinyMCE or create a new account.
  2. If you do not already have a key, start a free trial to create one.
  3. Once the key has been generated, go to API Key Manager, and click the manage button next to your new key.
  4. Follow their prompts to whitelist any IP and port combinations where you will be running this application.
  5. In app.yaml, set the MCE_KEY environment variable to your API key.
- TODO: Zip code API key info goes here

### Development Server
Once the libraries, database, database proxy, and API keys are setup the application can be started with `dev_appserver.py app.yaml`. Flask debugging is set when run locally although Google does not play nicely with this. 

## Deploying
Following the local setup will also prepare your application for deploying with a few caveats:
- Dependencies must be installed in the `lib/` directory (use `pip install -t lib -r requirements.txt`)
- Environment varibles must be also set in the `app.yaml` file (you can get away with just shell variables locally)

Deploy the application with `gcloud app deploy`. Take care of the datastore indices with `gcloud app deploy index.yaml`

### Indexes

Before you can use your application in production, you must also ensure that the indexes that the Datastore uses have been created. These configurations are in index.yaml; deploy them using `gcloud app deploy index.yaml`. This will trigger your application to rebuild its indexes so queries can be run.