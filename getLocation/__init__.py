import azure.functions as func
from gtts import gTTS
import os
from tempfile import NamedTemporaryFile
import pymongo
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    objectName = req.params.get('objectName')
    if not objectName:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            objectName = req_body.get('objectName')

    if objectName:
        # Generate the audio from the text
        client = pymongo.MongoClient("mongodb+srv://ECVuser:rrpZTW6tZh6LvgBg@clusterecv.8ubs7wd.mongodb.net/?retryWrites=true&w=majority&appName=ClusterECV")
        db = client["smARt-shopper"]
        collection = db["objects"]
        result = collection.find_one({"objectName": objectName})
        position = result.get("position", "Not found")
        text = "The " + objectName + " is at position " + str(position)
        out = {"text": text, "position": position}
        return func.HttpResponse(json.dumps(out), status_code=200)
        # Return the response with the audio file
        return func.HttpResponse(text, status_code=200)
    else:
        return func.HttpResponse(
             "Please pass a objectName on the query string or in the request body",
             status_code=400
        )
