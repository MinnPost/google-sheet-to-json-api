# Google Sheet to JSON API
An API to convert a Google Sheet to JSON

## Google Sheets setup

For both local and remote environments, you'll need to make sure the application has access to any Google Sheets data that it needs to load. In version 4 of the Sheets API, this happens through Service Accounts.

### Creating a new authentication

If you are authenticating this application with the Sheets API for the first time, you'll need to create a new Google Cloud project. Start by following [this guide from Google](https://developers.google.com/workspace/guides/create-project). When you've finished Google's steps, you should have a new project.

Our specific Google Sheets integration uses the [Sheetfu library](https://github.com/socialpoint-labs/sheetfu), which has [an authentication guide](https://github.com/socialpoint-labs/sheetfu/blob/master/documentation/authentication.rst) to finish this process. The screenshots are not necessarily up to date with the names Google uses for things.

Between these resources, you should follow these steps to create and access the authentication credentials:

1. Create a new Google Cloud Platform project.
1. Enable the Sheets and Drive APIs in the APIs & Services section of the Google Cloud Platform settings.
1. Create a Service Account in the IAM & Admin section of the Google Cloud Platform settings.
1. Download the new JSON-formatted key for that Service Account. Click the Actions menu for that account and choose the Manage keys option to create and download the key. Only use this key for one environment.

This new Service account will have an automatically-created email address. For this application, that email address must have at least Viewer-level access on any Google Sheets that it needs to access. It's best to give it that level of access on the folder level.

If this user is new or it is being given new access, it can take a few minutes for the changes to propogate.

### Accessing an existing authentication

If the Service Account user already exists in the Google Cloud Platform, you can access it at https://console.cloud.google.com/home/dashboard?project=[application-name].

If it hasn't been, you'll need your Google account added. An Administrator can do that at the correct dashboard URL by clicking "Add People to this Project."

Follow these steps to access the authentication credentials:

1. Once you have access to the project's dashboard, click "Go to project settings" in the Project info box.
1. Click Service Accounts in the IAM & Admin section of the Google Cloud Platform settings.
1. If there is more than one service account, find the correct one.
1. Click the Actions menu for that account and choose the Manage keys option.
1. Click Add Key, choose Create new key, and choose JSON as the Key type. Click the Create button and download the key for that Service Account. Only use this key for one environment.

Once you have downloaded the JSON file with the credentials, you will use the values from it in the `.env` file or in the project's Heroku settings. See the sections of this readme that cover authentication for Google Sheets. Once you've authenticated successfully, you don't have to keep the JSON file around, unless you'd like to have a backup.

## Redis setup

Before running the application, you'll need to run a Redis server for caching data. One way to do this is with Homebrew.

### Local setup

1. Run `brew update` then `brew install redis`
1. If you want Redis to start automatically on login, run `brew services start redis`. To stop it, run `brew services stop redis`. If you want to run Redis in a terminal shell instead, you can run `redis-server /usr/local/etc/redis.conf` instead of using brew service.
1. Test if Redis is running with the command `redis-cli ping`. Redis should respond with "PONG."
1. You shouldn't need a graphic interface for this project, but if you prefer to use one, [Medis](https://getmedis.com) is free on the Mac App Store.

### Production setup

To run Redis on Heroku, installing the free Heroku Redis add-on should be sufficient.

### Configuration

Use the following fields in your `.env` or in your Heroku settings.

- `CACHE_TYPE = "RedisCache"`
- `CACHE_REDIS_HOST = "redis"`
- `CACHE_REDIS_PORT = "6379"` (unless you are using a non-default port for Redis)
- `CACHE_REDIS_DB = "0"` (unless you need a separate Redis database. Redis creates databases in numeric order, so you can use other numbers)
- `CACHE_REDIS_URL = "redis://127.0.0.1:6379/0"` (make sure the `:6379` matches your port value, and that `/0` matches your Redis database number)
- `CACHE_DEFAULT_TIMEOUT = "500"`


## Amazon S3 setup

To push JSON data from this application to Amazon AWS, we use the `boto3` library.

### Configuration

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Fill in these values from the Amazon account.


## Application setup

### Set the Google Spreadsheet to load

Go to the Google spreadsheet you are using and copy the ID value from its URL. If the ID was `https://docs.google.com/spreadsheets/d/[spreadsheet-id]/edit#gid=809379382`, the ID would be `[spreadsheet-id]`. Use that value in your `.env` file and in the Heroku settings for the `SPREADSHEET_ID` field value.

### Local setup and development

1. Install `git`
1. Get the code: `git clone https://github.com/MinnPost/google-sheet-to-json-api.git`
1. Change the directory: `cd google-sheet-to-json-api`
1. Create a `.env` file based on the repository's `.env-example` file in the root of your project.
1. Run `pipenv install`.
1. Run `pipenv shell`
1. Run `flask run --host=0.0.0.0`. This creates a basic endpoint server at http://0.0.0.0:5000.

#### Local authentication for Google Sheets

Enter the configuration values from the JSON key downloaded above into the `.env` file's values for these fields:

- `SHEETFU_CONFIG_TYPE`
- `SHEETFU_CONFIG_PROJECT_ID`
- `SHEETFU_CONFIG_PRIVATE_KEY_ID`
- `SHEETFU_CONFIG_PRIVATE_KEY`
- `SHEETFU_CONFIG_CLIENT_EMAIL`
- `SHEETFU_CONFIG_CLIENT_ID`
- `SHEETFU_CONFIG_AUTH_URI`
- `SHEETFU_CONFIG_TOKEN_URI`
- `SHEETFU_CONFIG_AUTH_PROVIDER_URL`
- `SHEETFU_CONFIG_CLIENT_CERT_URL`

### Production setup and deployment

#### Code, Libraries and prerequisites

This application should be deployed to Heroku. If you are creating a new Heroku application, clone this repository with `git clone https://github.com/MinnPost/google-sheet-to-json-api.git` and follow [Heroku's instructions](https://devcenter.heroku.com/articles/git#creating-a-heroku-remote) to create a Heroku remote.

#### Production authentication for Google Sheets

In the project's Heroku settings, enter the configuration values from the production-only JSON key downloaded above into the values for these fields:

- `SHEETFU_CONFIG_TYPE`
- `SHEETFU_CONFIG_PROJECT_ID`
- `SHEETFU_CONFIG_PRIVATE_KEY_ID`
- `SHEETFU_CONFIG_PRIVATE_KEY`
- `SHEETFU_CONFIG_CLIENT_EMAIL`
- `SHEETFU_CONFIG_CLIENT_ID`
- `SHEETFU_CONFIG_AUTH_URI`
- `SHEETFU_CONFIG_TOKEN_URI`
- `SHEETFU_CONFIG_AUTH_PROVIDER_URL`
- `SHEETFU_CONFIG_CLIENT_CERT_URL`

## Application usage

Currently, this application has two endpoints:

- `/parser/` is the main endpoint. It accepts `GET` requests, and will return JSON of that Google sheet's data and cache it. If there is a customized JSON structure that has already been cached and has not expired, it will return that instead. A `GET` request supports these parameters on the URL:
    - `spreadsheet_id` is an ID of a Google Sheet that the application user can access.
    - `worksheet_names` is an optional parameter of hyphen-separated worksheet names, such as `Races-Candidates`. If it is left blank, the endpoint will assume it should look for `Sheet1`.
    - `skip_cache` is an optional parameter to bypass any previously cached data. With this parameter, data from the spreadsheet will override whatever might currently be cached, and will itself be cached.
- `/parser/custom-overwrite/` receives `POST` requests. It receives custom formatted JSON, caches it, and returns it. A `POST` request requires `appliation/json` as the `Content-Type` header and supports these parameters in the body:
    - `spreadsheet_id` is an ID of a Google Sheet that the application user can access.
    - `worksheet_names` is an optional list of worksheet names, such as `["Races", "Candidates"]`. If it is left out, the endpoint will assume it should look for `Sheet1`.
    - `cache_timeout` is an optional number of seconds for which the cache should last before it expires. If it left out, the cache will not expire (though Redis may delete it).
    - `output` is a full JSON output of the Google Sheet as it should be stored.
