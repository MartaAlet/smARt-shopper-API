from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from gtts import gTTS
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    objectName = req.params.get('objectName')
    # Assume objectName is valid for simplicity
    text = "Example text to convert to speech"
    tts = gTTS(text=text, lang='en')

    # Save to temp file
    tts.save('/tmp/temp.mp3')

    # Upload to Azure Blob Storage
    connect_str = os.getenv('DefaultEndpointsProtocol=https;AccountName=smartshopperapi;AccountKey=TjdbFCPCCFdn9TM8IfZ2vnBC74qcS4Yb+6FuOnTAqKxHptKTfA+20jPdpINAsuy7zMLiJMKqFKoS+AStYBxNiQ==;EndpointSuffix=core.windows.net')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container="audiofiles", blob="temp.mp3")

    with open('/tmp/temp.mp3', "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    # URL to access the blob
    url = blob_client.url
    return func.HttpResponse(f"File available at {url}", status_code=200)
