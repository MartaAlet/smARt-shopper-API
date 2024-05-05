from askAgent import taskManagement
import logging
import azure.functions as func
from tempfile import NamedTemporaryFile
import os
import speech_recognition as sr
import json

def transcribe_audio(audio_file_path):
    # Create a recognizer object
    recognizer = sr.Recognizer()
    text = ""
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        text = str(e)
    return text


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    taskDone = "No task done"
    taskResult = "No task result"
    try:
        # Check if the request contains multipart/form-data
        debug = req.headers.get('Content-Type', '')
        if not req.headers.get('Content-Type', '').startswith('multipart/form-data'):
            return func.HttpResponse(f"This function expects a multipart/form-data request with an audio file included. Debug: {debug}... {list(req.headers)}", status_code=400)
        
        # Process multipart/form-data using a robust method
        audiofile = req.files.get('audiofile')
        if not audiofile:
            return func.HttpResponse("No audio file found in the request.", status_code=400)
        
        # Save the audio file to a temporary file
        with NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audiofile.read())  # Write file content to temp file
            tmp_file_path = tmp_file.name  # Get the path to the temp file

        # Transcribe the audio
        transcription = transcribe_audio(tmp_file_path)
        manager = taskManagement.TaskManager(transcription)
        result = manager.perform_task()
        taskToDo = result[0]
        taskParameter = result[1]
        
        # Clean up the temporary file
        os.remove(tmp_file_path)
        out = {"taskName": taskToDo, "taskArgument": taskParameter}
        return func.HttpResponse(json.dumps(out), status_code=200)
    
    except Exception as e:
        return func.HttpResponse(f"Error processing the audio file: {e}", status_code=200)