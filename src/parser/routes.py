import json
from flask import json, Response, request, current_app
from src.extensions import cache
from src import spreadsheet
from src.parser import bp

@bp.route("/", methods=["GET"])
def parser():
    cache_timeout = current_app.config["CACHE_DEFAULT_TIMEOUT"]
    output = {}
    spreadsheet_id = request.args.get("spreadsheet_id", None)
    bypass_cache = request.args.get("bypass_cache", "false")
    cache_data = request.args.get("cache_data", "true")
    if spreadsheet_id != None:
        worksheet_slug = request.args.get("worksheet_names", "Sheet1")
        worksheet_names = worksheet_slug.split("-")
        custom_cache_key = spreadsheet_id + '-' + worksheet_slug + '-custom'
        cached_custom_output = cache.get(custom_cache_key)
        if cached_custom_output == None or bypass_cache == "true":
            cache_key = spreadsheet_id + '-' + worksheet_slug
            if bypass_cache == "true":
                cache.delete(custom_cache_key)
                cached_output = None
            else:
                cached_output = cache.get(cache_key)
            if cached_output == None or bypass_cache == "true" or cache_data == "false":
                if bypass_cache == "true":
                    cache.delete(cache_key)
                if cache_data == "false":
                    current_app.log.info('Cached data is not available. Try to load data from the spreadsheet but do not cache it.')
                    output = spreadsheet.parser(spreadsheet_id, worksheet_names, None)
                else:
                    current_app.log.info('Cached data is not available. Try to load data from the spreadsheet and cache it.')
                    output = spreadsheet.parser(spreadsheet_id, worksheet_names, cache_timeout)
                    cached_output = cache.set(cache_key, output, timeout=cache_timeout)
            else:
                current_app.log.info('Custom formatted data is not available but cached data is. Send it back for formatting.')
                output = cached_output
        else:
            current_app.log.info('Custom formatted data is cached. Send it back for display.')
            output = cached_custom_output            
    else:
        current_app.log.error('No spreadsheet ID is present.')
        output = {"No spreadsheet ID is present"}

    mime = 'application/json'
    ctype = 'application/json; charset=UTF-8'
    res = Response(response = output, status = 200, mimetype = mime)
    res.headers['Content-Type'] = ctype
    res.headers['Connection'] = 'keep-alive'
    return res


@bp.route("/custom-overwrite/", methods=['POST'])
def overwrite():
    output = {}
    cache_timeout = 0
    data = json.loads(request.data)
    spreadsheet_id = data["spreadsheet_id"]
    if "cache_timeout" in data:
        cache_timeout = data["cache_timeout"]
    if spreadsheet_id:
        if data["worksheet_names"]:
            worksheet_names = data["worksheet_names"]
        else:
            worksheet_names = {"Sheet1"}
        worksheet_slug = '-'.join(worksheet_names)
        cache_key = spreadsheet_id + '-' + worksheet_slug + '-custom'
        cached_output = cache.get(cache_key)
        if cached_output == None:
            output = data["output"]
            cached_output = cache.set(cache_key, output, timeout=cache_timeout)
        else:
            output = cached_output

    mime = 'application/json'
    ctype = 'application/json; charset=UTF-8'
    res = Response(response = output, status = 200, mimetype = mime)
    res.headers['Content-Type'] = ctype
    res.headers['Connection'] = 'keep-alive'
    return res
