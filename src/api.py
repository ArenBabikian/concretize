from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
CORS(app)

@app.post("/generate")
def generate():
    mapFileName = ""
    if 'map' in request.files and len(request.files['map'].filename) > 0:
        mapFile = request.files['map']
        mapFileName = secure_filename(mapFile.filename)
        mapFile.save(os.path.join(app.config['UPLOAD_FOLDER'], mapFileName))
    jsonData = request.get_json()
    constraints = jsonData['constraints']
    pass