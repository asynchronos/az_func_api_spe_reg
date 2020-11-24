import logging
from mimetypes import MimeTypes

import azure.functions as func
import mimetypes

def main(req: func.HttpRequest,context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "GET":
        filename = f"speech2text/upload.html"
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
            
            # print(f"{fl.filename} uploaded." 
            # + f"\n\nContent: \n{fl.read()})"

            respMSG = az_speech_regconite()

            return func.HttpResponse(
                respMSG(fl)
                ,status_code=200
            )

def read_file(file):
    return f"{file.filename} uploaded." + f"\n\nContent: \n{file.read()}"

def leang_ai(file):
    # add your code here 
    import azure.cognitiveservices.speech as speechsdk
    import time
    import datetime

    # Creates an instance of a speech config with specified subscription key and service region.
    # Replace with your own subscription key and region identifier from here: https://aka.ms/speech/sdkregion
    speech_key, service_region = "53670c8c8ad14415863b7206bbccb48c", "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

    # Creates an audio configuration that points to an audio file.
    # Replace with your own audio filename.
    audio_filename = "see_you_again.wav"
    audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_input)

    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

    # Creates a recognizer with the given settings
    speech_config.speech_recognition_language="en-US"
    speech_config.request_word_level_timestamps()
    speech_config.enable_dictation()
    speech_config.output_format = speechsdk.OutputFormat(1)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    #result = speech_recognizer.recognize_once()
    all_results = []

    #https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.recognitionresult?view=azure-python
    def handle_final_result(evt):
        all_results.append(evt.result.text+"\n") 
        
    done = False

    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        global done
        done= True

    #Appends the recognized text to the all_results variable. 
    speech_recognizer.recognized.connect(handle_final_result) 

    #Connect callbacks to the events fired by the speech recognizer & displays the info/status
    #Ref:https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.eventsignal?view=azure-python   
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)

    speechText = "Your Result."
    return speechText

def az_speech_regconite():
    return read_file
    #return leang_ai