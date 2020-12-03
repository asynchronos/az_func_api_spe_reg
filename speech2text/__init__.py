import logging
from mimetypes import MimeTypes

import azure.functions as func
import mimetypes
from azure.functions._thirdparty.werkzeug.datastructures import FileStorage
from azure.storage.blob import BlobServiceClient, BlobClient
import os
from azure.functions._thirdparty.werkzeug.utils import secure_filename

CONFIG_MAX_CONTENT_LENGTH = 1024*1024
CONFIG_UPLOAD_EXTENSIONS = [".wav",".txt"]
CONFIG_UPLOAD_PATH = "uploads"
CONFIG_RESULT_PATH = "results"

def main(req: func.HttpRequest,outputBlob: func.Out[func.InputStream],context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "GET":
        filename = f"{context.function_name}/upload.html"
        with open(filename,"rb") as f:
            return func.HttpResponse(f.read(),mimetype='text/html')        

    if req.method == "POST":
        if req.files:
            try:
                fl = req.files.get("file")
            except ValueError:
                return func.HttpResponse(
                    "file not found."
                    ,status_code=200
                )
            
            uploadPath = os.path.join(context.function_directory, CONFIG_UPLOAD_PATH)
            try:
                # os.rmdir(uploadPath)
                os.makedirs(uploadPath)
            except OSError:
                print ("Creation of the directory %s failed" % uploadPath)
            else:
                print ("Successfully created the directory %s" % uploadPath)

            resultPath = os.path.join(context.function_directory, CONFIG_RESULT_PATH)
            try:
                # os.rmdir(resultPath)
                os.makedirs(resultPath)
            except OSError:
                print ("Creation of the directory %s failed" % resultPath)
            else:
                print ("Successfully created the directory %s" % resultPath)

            # outputBlob.set(fl.read())
            # input = outputBlob.get().uri
            # #input = outputBlob.get()   
            
            filename = secure_filename(fl.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in CONFIG_UPLOAD_EXTENSIONS:
                return func.HttpResponse("Abort",status_code=400)
            
            if file_ext == ".txt":
                # fl.save(os.path.join(context.function_directory, CONFIG_UPLOAD_PATH, filename))
                # with open(os.path.join(context.function_directory, CONFIG_UPLOAD_PATH, filename),"r") as fl:
                    result = f"{filename} uploaded." + f"\n\nContent: \n{fl.read()}"
            else:    
                savefile = os.path.join(context.function_directory, CONFIG_UPLOAD_PATH, filename)            
                fl.save(savefile)
                outfile = os.path.join(context.function_directory
                                    , CONFIG_RESULT_PATH
                                    , "translate_" + filename +"_"+ context.invocation_id + ".txt")
                result = leang_ai(filename=savefile,outfile=outfile)

            #respMSG = az_speech_regconite()
            return func.HttpResponse(
                #respMSG(fl)
                result
                ,status_code=200
            )

def leang_ai(filename, outfile):
    # add your code here 
    import azure.cognitiveservices.speech as speechsdk
    import time
    import datetime

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
    speech_key, service_region = os.environ["SPEECH_KEY"], os.environ["SERVICE_REGION"]
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # Creates an audio configuration that points to an audio file.
    # Replace with your own audio filename.
    #audio_filename = "see_you_again2.wav"
    audio_filename = filename
    audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)

    # Creates a recognizer with the given settings
    speech_config.speech_recognition_language="en-US"
    speech_config.request_word_level_timestamps()
    speech_config.enable_dictation()
    speech_config.output_format = speechsdk.OutputFormat(1)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    #result = speech_recognizer.recognize_once()
    all_results = []

    #https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.recognitionresult?view=azure-python
    def handle_final_result(evt):
        all_results.append(evt.result.text+"\n") 
        with open(outfile,"a") as fl:
            fl.writelines(evt.result.text+"\n")
            fl.save(outfile)
        
    done = False

    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition_async()
        nonlocal done
        done= True

    #Appends the recognized text to the all_results variable. 
    speech_recognizer.recognized.connect(handle_final_result) 

    #Connect callbacks to the events fired by the speech recognizer & displays the info/status
    #Ref:https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.eventsignal?view=azure-python   
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    #speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    #speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    #speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)

    #speechText = "Your Result."
    return ' '.join(map(str,all_results))

def az_speech_regconite():
    #return read_file
    return leang_ai