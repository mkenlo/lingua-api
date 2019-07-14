import json


def jsonify(data):
    """transform into a json object the input data"""
    data = data.decode("utf8")
    data = data.replace("\n","").replace("\t","")
    return json.loads(data)