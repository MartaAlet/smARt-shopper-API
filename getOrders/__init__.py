import logging
import pymongo
import azure.functions as func
import json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    client = pymongo.MongoClient("mongodb+srv://ECVuser:rrpZTW6tZh6LvgBg@clusterecv.8ubs7wd.mongodb.net/?retryWrites=true&w=majority&appName=ClusterECV")
    db = client["smARt-shopper"]
    collection = db["tasks"]
    result = collection.find({}, {"orderID": 1, "description": 1, "_id": 0})
    
    result_list = list(result)
    
    out = json.dumps(result_list, ensure_ascii=False).encode('utf8')

    return func.HttpResponse(out, status_code=200)

