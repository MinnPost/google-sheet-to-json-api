import json
from flask import json, Response, request, current_app
from src.authorize import bp
from flask_jwt_extended import create_access_token

@bp.route("/", methods=["POST"])
def create_token():
    valid_api_keys = current_app.config["VALID_API_KEYS"]
    output = {}
    data = json.loads(request.data)
    user_api_key = data["api_key"]
    if user_api_key is None or len(valid_api_keys) == 0:
        # the user was not found on the database
        output = {"msg": "Missing api key"}
        status = 401
    elif user_api_key not in valid_api_keys:
        # the user was not found on the database
        output = {"msg": "Invalid api key"}
        status = 401
    else:
        # create a new token with the user id inside
        access_token = create_access_token(identity=user_api_key)
        output = { "token": access_token, "api_key": user_api_key }
        status = 200

    mime = 'application/json'
    ctype = 'application/json; charset=UTF-8'
    res = Response(response = json.dumps(output), status = status, mimetype = mime)
    res.headers['Content-Type'] = ctype
    res.headers['Connection'] = 'keep-alive'
    return res
