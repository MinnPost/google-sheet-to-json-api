import json
from flask import json, Response, request, current_app
from src.extensions import cache
from src import spreadsheet
from src.parser import bp

@bp.route("/", methods=['POST'])
@cache.cached(timeout=30, query_string=True)
def parser():
    output = {}
    data = json.loads(request.data)
    spreadsheet_id = data["spreadsheet_id"]
    if spreadsheet_id:
        worksheet_names = data["worksheet_names"]
        output = spreadsheet.parser(spreadsheet_id, worksheet_names)        

    mime = 'application/json'
    ctype = 'application/json; charset=UTF-8'
    res = Response(response = output, status = 200, mimetype = mime)
    res.headers['Content-Type'] = ctype
    res.headers['Connection'] = 'keep-alive'
    return res
