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

def leang_ai(file):
    # add your code here 
    

    speechText = "Your Result."
    return speechText

def az_speech_regconite():
    return leang_ai