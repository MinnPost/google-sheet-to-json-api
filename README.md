# Google Sheet to JSON API
A Flask-based API to convert a Google Sheet to JSON. Structurally, this application is based on [this example](https://github.com/nebularazer/flask-celery-example), which itself is a restructuring of [this example](https://github.com/miguelgrinberg/flask-celery-example) and its [accompanying article](https://blog.miguelgrinberg.com/post/using-celery-with-flask).

## Google Sheets

For both local and remote environments, you'll need to make sure the application has access to any Google Sheets data that it needs to load. In version 4 of the Sheets API, this happens through Service Accounts.

### Creating a new Google Sheets authentication

If you are authenticating this application with the Sheets API for the first time, you'll need to create a new Google Cloud project. Start by following [this guide from Google](https://developers.google.com/workspace/guides/create-project). When you've finished Google's steps, you should have a new project.

Our specific Google Sheets integration uses the [Sheetfu library](https://github.com/socialpoint-labs/sheetfu), which has [an authentication guide](https://github.com/socialpoint-labs/sheetfu/blob/master/documentation/authentication.rst) to finish this process. The screenshots are not necessarily up to date with the names Google uses for things.

Between these resources, you should follow these steps to create and access the authentication credentials:

1. Create a new Google Cloud Platform project.
1. Enable the Sheets and Drive APIs in the APIs & Services section of the Google Cloud Platform settings.
1. Create a Service Account in the IAM & Admin section of the Google Cloud Platform settings.
1. Download the new JSON-formatted key for that Service Account. Click the Actions menu for that account and choose the Manage keys option to create and download the key. Only use this key for one environment.

This new Service account will have an automatically-created email address. For this application, that email address must have at least Viewer-level access on any Google Sheets that it needs to access. It's best to give it that level of access on the folder level.

If this user is new or it is being given new access, it can take a few minutes for the changes to propogate.

### Accessing an existing Google Sheets authentication

If the Service Account user already exists in the Google Cloud Platform, you can access it at https://console.cloud.google.com/home/dashboard?project=[application-name].

If it hasn't been, you'll need your Google account added. An Administrator can do that at the correct dashboard URL by clicking "Add People to this Project."

Follow these steps to access the authentication credentials:

1. Once you have access to the project's dashboard, click "Go to project settings" in the Project info box.
1. Click Service Accounts in the IAM & Admin section of the Google Cloud Platform settings.
1. If there is more than one service account, find the correct one.
1. Click the Actions menu for that account and choose the Manage keys option.
1. Click Add Key, choose Create new key, and choose JSON as the Key type. Click the Create button and download the key for that Service Account. Only use this key for one environment.

Once you have downloaded the JSON file with the credentials, you will use the values from it in the `.env` file or in the project's Heroku settings. See the sections of this readme that cover authentication for Google Sheets. Once you've authenticated successfully, you don't have to keep the JSON file around, unless you'd like to have a backup.

### Local authentication for Google Sheets

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

### Production authentication for Google Sheets

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

## Storage

This API supports storing JSON in either the application's Redis instance (whether locally or on Heroku) or in an Amazon S3 bucket. If you do not enable S3 usage, Redis will be used by default.

### Redis

Before running the application, you'll need to run a Redis server for caching data. One way to do this is with Homebrew.

#### Local setup

1. Run `brew update` then `brew install redis`
1. If you want Redis to start automatically on login, run `brew services start redis`. To stop it, run `brew services stop redis`. If you want to run Redis in a terminal shell instead, you can run `redis-server /usr/local/etc/redis.conf` instead of using brew service.
1. Test if Redis is running with the command `redis-cli ping`. Redis should respond with "PONG."
1. You shouldn't need a graphic interface for this project, but if you prefer to use one, [Medis](https://getmedis.com) is free on the Mac App Store.

#### Production setup

To run Redis on Heroku, installing the free Heroku Redis add-on should be sufficient.

#### Redis configuration

Use the following fields in your `.env` or in your Heroku settings.

- `CACHE_TYPE = "RedisCache"`
- `CACHE_REDIS_HOST = "redis"`
- `CACHE_REDIS_PORT = "6379"` (unless you are using a non-default port for Redis)
- `CACHE_REDIS_DB = "0"` (unless you need a separate Redis database. Redis creates databases in numeric order, so you can use other numbers)
- `CACHE_REDIS_URL = "redis://127.0.0.1:6379/0"` (make sure the `:6379` matches your port value, and that `/0` matches your Redis database number)
- `CACHE_DEFAULT_TIMEOUT = "500"`


### Amazon S3

To push JSON data from this application to Amazon AWS, we use the `boto3` library.

#### Amazon S3 configuration

To upload a file to S3, fill in these `.env` values to match your S3 account. If S3 is enabled, URLs for your files will be `https://s3.amazonaws.com/[your bucket]/[your folder]/[this spreadsheet's cachekey].json`.

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_BUCKET`
- `AWS_FOLDER`
- `USE_AWS_S3` use "true" or "false" for this; it will be converted to lowercase if you forget. "false" is the default value for this setting.


## Application authentication

We use a basic setup of [Flask-JWT-Extended](https://github.com/vimalloc/flask-jwt-extended) to manage application access.

To generate API keys, run this code:

```python
import secrets
secrets.token_hex(64)
```

Do this for each valid API key that an application can use to access this API.

### Managing API keys

Store a list of valid API keys in the `.env` file or in Heroku configuration.

- `VALID_API_KEYS = '["key1", "key2"]'`

### JWT Secret

Store a single secret key in the `JWT_SECRET_KEY` field of the `.env` file or in Heroku configuration.

## Running the application

### Additional configuration

There are a few general `.env` variables not already discussed. You can see these settings, and their default values (or the kind of value they expect), in the repository's `.env-example` file.

### Local setup and development

1. Install `git`
1. Get the code: `git clone https://github.com/MinnPost/google-sheet-to-json-api.git`
1. Change the directory: `cd google-sheet-to-json-api`
1. Create a `.env` file based on the repository's `.env-example` file in the root of your project.
1. Run `pipenv install`.
1. Run `pipenv shell`
1. Run `flask run --host=0.0.0.0`. This creates a basic endpoint server at http://0.0.0.0:5000.

### Production setup and deployment

#### Code, Libraries and prerequisites

This application should be deployed to Heroku. If you are creating a new Heroku application, clone this repository with `git clone https://github.com/MinnPost/google-sheet-to-json-api.git` and follow [Heroku's instructions](https://devcenter.heroku.com/articles/git#creating-a-heroku-remote) to create a Heroku remote.

## Application usage

Currently, this application has three endpoints:

- `authorize` is used to get a token from a valid API key. The token is then required by the other endpoints. This endpoint accepts `POST` requests.
- `/parser/` is the main endpoint. It accepts `GET` requests, and will return JSON of that Google sheet's data and cache it. If there is a customized JSON structure that has already been cached and has not expired, it will return that instead.
- `/parser/custom-overwrite/` receives `POST` requests. It receives custom formatted JSON, caches it, and returns it. A `POST` request requires `appliation/json` as the `Content-Type` header.

### Authorization parameters

- `api_key` is *required* in the `POST` body for requests to `authorize`. A request with a valid API key returns a `token`.
- `token` is *required* as an `Authorization` header value on `/parser/` and `/parser/custom-overwrite/` requests. A request without a valid token in that header will fail. It can generally be passed to a `GET` or `POST` endpoint after it is written like this:

```python
authorized_headers = {
    "Authorization": f"Bearer {valid_token_value}"
}
```

### Data parameters

Both URL endpoints support many of the same data parameters, but they get passed on the URL (in the case of a `GET` endpoint) or in the post body (in the case of a `POST` endpoint). Most parameters are usable by both endpoints, but if they are end-point specific that will be noted.

#### For all requests
- `spreadsheet_id` is a *required* ID of a Google Sheet that the application user can access.
- `worksheet_names` is an optional parameter of worksheet names, such as `Races|Candidates`. If it is left blank, the endpoint will load the first worksheet in the spreadsheet. If there are multiple worksheets provided, they will be sorted alphabetically to keep consistency.

#### For `custom-overwrite` requests only
- `output` is a full, customized JSON output of the modified Google Sheet data as it should be stored. It is only accepted on the `/parser/custom-overwrite` endpoint as a `POST` parameter.

#### For S3 storage only
- `external_use_s3` is an optional parameter that takes a value of "true" or "false", and determines whether JSON data is saved to Amazon S3 instead of in Redis. A value for this parameter will override the default setting in the `.env` file.

#### For cache storage only

All of these parameters are specific to the Redis cache. They are all optional, but have default values.

- `bypass_cache` takes a value of "true" or "false". "false" is the default value. If the value is "true" the application will not check the Redis cache for any stored data, but will attempt to parse the Google Sheet directly and return its data.
- `delete_cache` takes a value of "true" or "false". "false" is the default value. If the value is "true" the application will delete the cached data for the Google Sheet.
- `cache_data` takes a value of "true" or "false". "true" is the default value. If the value is "false" the application will not store data for the Google Sheet in the cache.
- `cache_timeout` takes the number of seconds that the cache should last before it expires. If present, this will override the default value from the `.env` file. This value only has an effect on requests where data is actually being cached.    
