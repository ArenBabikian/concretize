import os
from flask import Flask, current_app, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from src.controller import *
import traceback

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER_NAME = 'uploads'
app.config['UPLOAD_FOLDER'] = f'./{UPLOAD_FOLDER_NAME}'

@app.post("/generate")
def generate():
    jsonData = request.get_json()
    constraints = jsonData['constraints']
    args = AutoObject(jsonData['args'])
    args.upload_folder = app.config['UPLOAD_FOLDER']
    # TODO: Support upload of map files
    try:
        diagramFileNames = generateFromSpecs(constraints, args)
        if diagramFileNames is None or len(diagramFileNames) == 0:
            return {
                "error": "Could not satisfy constraints"
            }
        else:
            return {
                "diagram_file_names": diagramFileNames
            }
    except Exception as e:
        print(traceback.format_exc())
        return {
            "error": str(e)
        }
    

@app.get("/downloads/<filename>")
def download(filename):
    abspath = os.path.join(current_app.root_path, f"/{UPLOAD_FOLDER_NAME}")
    return send_file(f".{abspath}/{filename}")

class AutoObject(object):   
    def __init__(self, d: dict):
        for key, value in d.items():
            setattr(self, key, value)
