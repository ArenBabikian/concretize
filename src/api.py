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

# TODO ../output is hardcoded for now
UPLOAD_FOLDER_NAME = '../output/scenarios'
SIM_FOLDER_NAME = '../output/simulation'
app.config['UPLOAD_FOLDER'] = f'./{UPLOAD_FOLDER_NAME}'

@app.post("/generate")
def generate():
    jsonData = request.get_json()
    constraints = jsonData['constraints']
    args = AutoObject(jsonData['args'])
    args.upload_folder = app.config['UPLOAD_FOLDER']
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    args.save_path_sim = f"./{SIM_FOLDER_NAME}"
    Path(args.save_path_sim).mkdir(parents=True, exist_ok=True)

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
    print(f"Absolute path: {abspath}")
    return send_file(f"./{abspath}/{filename}")

@app.get("/simulate/<filename>")
def simulate(filename):
    try:
        # TODO improve this
        simulateSolution(filename)
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
