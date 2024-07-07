import os
from flask import Flask, current_app, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from src.controller import *
import traceback
from pathlib import Path

# TODO refactor this into a seperate folder
app = Flask(__name__)
CORS(app)

@app.post("/generate")
def generate():
    jsonData = request.get_json()
    constraints = jsonData['constraints']
    args = AutoObject(jsonData['args'])

    # TODO: Support upload of map files
    try:
        [uploadFolderName, diagramFileNames] = generateFromSpecs(constraints, args)
        app.config['UPLOAD_FOLDER'] = uploadFolderName
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
    abspath = os.path.join(current_app.root_path, f"/{app.config['UPLOAD_FOLDER']}")
    print(f"Absolute path: {abspath}")
    return send_file(f"./{abspath}/{filename}")

@app.post("/simulate/<filename>")
def simulate(filename):
    try:
        # TODO improve this
        jsonData = request.get_json()
        constraints = jsonData['constraints']

        simulateSolution(filename, constraints)
        
        return {
            "message": f"Simulated {filename}"
        }
    except Exception as e:
        print(traceback.format_exc())
        return {
            "error": str(e)
        }

class AutoObject(object):   
    def __init__(self, d: dict):
        for key, value in d.items():
            setattr(self, key, value)
