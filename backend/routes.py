from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

def match(item, target_id):
    matches = [item for item in data if item.get("id") == target_id]
    return matches

def generate_id(item):
    existing_ids = {item["id"] for item in data}
    new_id = 1
    while new_id in existing_ids:
        new_id += 1
    return new_id

def find_index(item, target_id):
    index = next((i for i, obj in enumerate(item) if obj["id"] == target_id), -1)
    return index

######################################################################
# RETURN HEALTH OF THE APP
######################################################################
@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200


######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################
@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    """return length of data"""
    if data:
        picture_url = []
        for picture in data:
            picture_url.append(picture["pic_url"])
        return jsonify(picture_url), 200
    return {"message": "Internal server error"}, 500


######################################################################
# GET A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    if data and id:
        matches = match(data, id)
        if len(matches) == 0:
            return {"message": "Picture does not exist"}, 404
        elif len(matches) == 1:
            return jsonify(matches[0]), 200
        else:
            return {"message": "Internal server error"}, 500
    return {"message": "Internal server error"}, 500


######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    json_data = request.get_json()
    if data and json_data:
        id = json_data["id"]
        matches = match(data, id) 
        if len(matches) == 0:
            data.append(json_data)
            return jsonify(json_data), 201
        else:
            new_id = generate_id(data)
            json_data["id"] = new_id
            # data.append(json_data)
            return {"Message": f"picture with id {id} already present"}, 302
    return {"message": "Internal server error"}, 500


######################################################################
# UPDATE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    json_data = request.get_json()
    if data and json_data and id:
        matches = match(data, id)
        if len(matches) == 1:
            index = find_index(data, id)
            data[index] = json_data
            return {"success": "picture updated"}, 200
    return {"message": "Internal server error"}, 500


######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    if data and id:
        matches = match(data, id)
        if len(matches) == 0:
            return {"message": "Picture does not exist"}, 404
        elif len(matches) == 1:
            index = find_index(data, id)
            try:
                data.pop(index)
                return {"success": "picture deleted"}, 204
            except:
                return {"message": "Picture does not exist"}, 404
        else:
            return {"message": "Internal server error"}, 500
    return {"message": "Internal server error"}, 500
