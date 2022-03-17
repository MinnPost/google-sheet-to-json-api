import json
from flask import json, Response, request, current_app
from src.storage import Storage
from src import spreadsheet
from src.parser import bp
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

@bp.route("/", methods=["GET"])
def parser():
    storage = Storage(request.args)
    output = {}
    spreadsheet_id = request.args.get("spreadsheet_id", None)
    if spreadsheet_id != None:
        worksheet_names_slug = request.args.get("worksheet_names", "")
        worksheet_keys_slug = request.args.get("worksheet_keys", "")
        worksheet_names = [""]
        worksheet_keys = [""]
        if worksheet_names_slug != "":
            worksheet_names = worksheet_names_slug.split(current_app.config["WORKSHEET_NAME_SEPARATOR"])
            worksheet_names.sort()
            worksheet_names_slug = '-' + worksheet_names_slug
            key = spreadsheet_id + worksheet_names_slug
        elif worksheet_keys_slug != "":
            worksheet_keys = worksheet_keys_slug.split(current_app.config["WORKSHEET_NAME_SEPARATOR"])
            worksheet_keys.sort()
            worksheet_keys_slug = '-' + worksheet_keys_slug
            key = spreadsheet_id + worksheet_keys_slug
        else:
            key = spreadsheet_id
        output = storage.get(key)
        if output == None:
            current_app.log.info(f"Stored data for {key} is not available. Try to load data from the spreadsheet.")
            data = spreadsheet.parser(spreadsheet_id, worksheet_names, worksheet_keys)
            output = storage.save(key, data)
    else:
        current_app.log.error('No spreadsheet ID is present.')
        output = {"No spreadsheet ID is present"}

    mime = "application/json"
    ctype = "application/json; charset=UTF-8"
    res = Response(response = output, status = 200, mimetype = mime)
    res.headers["Content-Type"] = ctype
    res.headers["Connection"] = "keep-alive"
    res.headers["Access-Control-Allow-Origin"] = "*"
    return res


@bp.route("/custom-overwrite/", methods=["POST"])
@jwt_required()
def overwrite():
    current_api_key = get_jwt_identity()
    current_app.log.info(f"Current API key is {current_api_key}")
    storage = Storage(request.data, "POST")
    output = {}
    data = json.loads(request.data)
    spreadsheet_id = data["spreadsheet_id"]
    if spreadsheet_id:
        if "worksheet_names" in data:
            worksheet_names = data["worksheet_names"]
            worksheet_names.sort()
            worksheet_names_slug = current_app.config["WORKSHEET_NAME_SEPARATOR"].join(worksheet_names)
            key = spreadsheet_id + "-" + worksheet_names_slug
        elif "worksheet_keys" in data:
            worksheet_keys = data["worksheet_keys"]
            worksheet_keys.sort()
            worksheet_keys_slug = current_app.config["WORKSHEET_NAME_SEPARATOR"].join(worksheet_keys)
            key = spreadsheet_id + "-" + worksheet_keys_slug
        else:
            key = spreadsheet_id

        key = key + "-custom"
        output = storage.get(key)
        if output == None:
            current_app.log.info(f"Stored data for {key} is not available. Load data from the JSON request.")
            output = data["output"]
            output = storage.save(key, output)

    mime = 'application/json'
    ctype = 'application/json; charset=UTF-8'
    res = Response(response = output, status = 200, mimetype = mime)
    res.headers['Content-Type'] = ctype
    res.headers["Connection"] = "keep-alive"
    res.headers["Access-Control-Allow-Origin"] = "*"
    return res
