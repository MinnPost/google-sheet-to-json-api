import json
from flask import json, Response, request, current_app
from src.storage import Storage
from src import spreadsheet
from src.parser import bp

@bp.route("/", methods=["GET"])
def parser():
    storage = Storage(request.args)
    output = {}
    spreadsheet_id = request.args.get("spreadsheet_id", None)
    if spreadsheet_id != None:
        worksheet_slug = request.args.get("worksheet_names", "Sheet1")
        worksheet_names = worksheet_slug.split("-")
        worksheet_names.sort()
        key = spreadsheet_id + '-' + worksheet_slug
        output = storage.get(key)
        if output == None:
            current_app.log.info(f"Stored data for {key} is not available. Try to load data from the spreadsheet.")
            data = spreadsheet.parser(spreadsheet_id, worksheet_names)
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
def overwrite():
    storage = Storage(request.data, "POST")
    output = {}
    data = json.loads(request.data)
    spreadsheet_id = data["spreadsheet_id"]
    if spreadsheet_id:
        if data["worksheet_names"]:
            worksheet_names = data["worksheet_names"]
        else:
            worksheet_names = {"Sheet1"}
        worksheet_names.sort()
        worksheet_slug = '-'.join(worksheet_names)
        key = spreadsheet_id + '-' + worksheet_slug + "-custom"
        output = storage.get(key)
        if output == None:
            current_app.log.info(f"Stored data for {key} is not available. Load data from the JSON request.")
            output = data["output"]
            output = storage.save(key, output)

    mime = 'application/json'
    ctype = 'application/json; charset=UTF-8'
    res = Response(response = output, status = 200, mimetype = mime)
    res.headers['Content-Type'] = ctype
    res.headers['Connection'] = 'keep-alive'
    return res


@bp.route("/push-s3", methods=['GET'])
def push_to_s3():
  output = spreadsheet.parser()
  s3 = storage.send_to_s3(output)
  return "Uploaded candidate-tracker.json to S3"
