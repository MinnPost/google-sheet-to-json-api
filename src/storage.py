import json
import datetime
from datetime import timedelta
import boto3
from src.extensions import cache
from flask import current_app

class Storage(object):

    def __init__(self, args, method = "GET"):
        self.args = args
        self.use_aws_s3 = current_app.config["USE_AWS_S3"]
        if method == "GET":
            self.external_use_s3 = args.get("external_use_s3", "false")
        else:
            self.external_use_s3 = "false"
            if "external_use_s3" in args:
                self.external_use_s3 = args["external_use_s3"]
        self.class_to_use = self.check_method()


    def check_method(self):
        class_to_use = CacheStorage(self.args)
        try_to_use_s3 = False
        can_use_s3 = False
        if self.external_use_s3 == "true" or self.use_aws_s3 == "true":
            try_to_use_s3 = True
        if try_to_use_s3 == True:
            s3_instance = S3Storage(self.args)
            can_use_s3 = s3_instance.check_config()
        if try_to_use_s3 == True and can_use_s3 == True:
            class_to_use = s3_instance
        return class_to_use


    def save(self, key, data):
        class_to_use = self.class_to_use
        output = class_to_use.save(key, data)
        return output


    def get(self, key):
        class_to_use = self.class_to_use
        output = class_to_use.get(key)
        return output


class S3Storage(object):

    def __init__(self, args = None):
        self.domain = current_app.config["S3_DOMAIN_ROOT"]
        self.bucket = current_app.config["AWS_BUCKET"]
        self.folder = current_app.config["AWS_FOLDER"]
        self.aws_access_key = current_app.config["AWS_ACCESS_KEY_ID"]
        self.aws_secret_key = current_app.config["AWS_SECRET_ACCESS_KEY"]

    
    def check_config(self):
        valid = True
        if self.aws_access_key == "" or self.aws_secret_key == "":
            valid = False
        if self.bucket == "" or self.folder == "":
            valid = False
        return valid
    
    
    def save(self, key, data):
        file_path = f"{self.folder}{key}.json"
        file_url = f"{self.domain}{self.bucket}/{file_path}"
        current_app.log.info(f"Store data in S3. The url is {file_url}.")
        data["file_url"] = file_url
        output = json.dumps(data, default=str)
        s3 = boto3.client('s3')
        result = s3.put_object(Bucket=self.bucket, 
                        Key=file_path, 
                        Body=output,
                        ContentType='application/json; charset=UTF-8',
                        ACL="public-read")
        if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            output = {"An error has occurred in uploading to S3."}
        return output


    def get(self, key):
        return None


class CacheStorage(object):

    def __init__(self, args, method = "GET"):
        self.cache_timeout = current_app.config["CACHE_DEFAULT_TIMEOUT"]
        if method == "GET":
            self.bypass_cache = args.get("bypass_cache", "false")
            self.cache_data = args.get("cache_data", "true")
            self.cache_timeout = int(args.get("cache_timeout", self.cache_timeout))
        else:
            self.bypass_cache = "false"
            self.cache_data = "true"
            if "bypass_cache" in args:
                self.bypass_cache = args["bypass_cache"]
            if "cache_data" in args:
                self.cache_data = args["cache_data"]


    def save(self, key, data):
        current_app.log.info(f"Store data in the cache. The key is {key} and the timeout is {self.cache_timeout}.")
        if self.cache_data == "true":
            if self.cache_timeout is not None and self.cache_timeout != 0:
                data["cache_timeout"] = data["generated"] + timedelta(seconds=int(self.cache_timeout))
            elif self.cache_timeout == 0:
                data["cache_timeout"] = 0
        output = json.dumps(data, default=str)
        if self.cache_data == "true":
            cache.set(key, output, timeout=self.cache_timeout)
        return output


    def get(self, key):
        custom_cache_key = key + '-custom'
        if self.cache_data == "false" or self.bypass_cache == "true":
            output = None
            current_app.log.info(f"Cached data for {key} is not available.")
            if self.bypass_cache == "true":
                cache.delete(key)
                cache.delete(custom_cache_key)
            return output
        
        output = cache.get(custom_cache_key)
        if output == None:
            output = cache.get(key)
            if output != None:
                current_app.log.info(f"Get data from the cache. The key is {key}. Send it back for display.")
        else:
            current_app.log.info(f"Get data from the cache. The key is {custom_cache_key}. Send it back for display.")
        return output
