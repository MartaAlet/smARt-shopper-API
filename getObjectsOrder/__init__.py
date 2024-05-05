import logging

import azure.functions as func
import pymongo
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('orderID')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('orderID')

    if name:
        client = pymongo.MongoClient("mongodb+srv://ECVuser:rrpZTW6tZh6LvgBg@clusterecv.8ubs7wd.mongodb.net/?retryWrites=true&w=majority&appName=ClusterECV")
        db = client["smARt-shopper"]
        collection = db["tasks"]
        result = collection.find_one({"orderID": name}, {"objects": 1, "_id": 0})
        if result:
            objects = result.get("objects", [])
            objects_collection = db["objects"]
            objects_found = []
            for obj in objects:
                obj_result = objects_collection.find_one({"objectName": obj}, {"_id": 0})
                if obj_result:
                    print(f"Object: {obj_result.get('name')}, Position: {obj_result.get('position')}")
                    objects_found.append(obj_result)
                else:
                    print(f"Object with ID {obj} not found in the 'objects' collection")
                    objects_found.append({"objectName": obj, "position": "Not found", "stock": "Not found"})
            return func.HttpResponse(json.dumps(objects_found), status_code=200)
        return func.HttpResponse(f"Order {name} not found in the list of orders", status_code=200)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a orderID in the query string or in the request body.",
             status_code=200
        )
