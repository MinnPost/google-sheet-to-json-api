import json
from flask import json, Response, request, current_app
from src.extensions import cache
from src import spreadsheet
from src.parser import bp

@bp.route("/", methods=['POST'])
def parser():
    cache_timeout = current_app.config["CACHE_DEFAULT_TIMEOUT"]
    output = {}
    if request.data:
        data = json.loads(request.data)
        spreadsheet_id = data["spreadsheet_id"]
        if spreadsheet_id:
            if data["worksheet_names"]:
                worksheet_names = data["worksheet_names"]
            else:
                worksheet_names = {"Sheet1"}
            worksheet_slug = '-'.join(worksheet_names)
            custom_cache_key = spreadsheet_id + '-' + worksheet_slug + '-custom'
            cached_custom_output = cache.get(custom_cache_key)
            if cached_custom_output == None:
                cache_key = spreadsheet_id + '-' + worksheet_slug
                cached_output = cache.get(cache_key)
                if cached_output == None:
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
    else:
        current_app.log.error('No request data is present.')
        output = {"No request data is available"}

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
