import os
from flask import Flask, current_app, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import controller

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
CORS(app)

@app.post("/generate")
def generate():
    jsonData = request.get_json()
    constraints = jsonData['constraints']
    args = jsonData['args']
    args.upload_folder = app.config['UPLOAD_FOLDER']
    # TODO: Support upload of map files
    diagramFileName = controller.generateFromSpecs(constraints, args)
    return {
        "diagram_file_name": diagramFileName
    }

@app.get("/downloads/<filename>")
def download(filename):
    uploadAbsPath = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploadAbsPath, filename=filename)
    