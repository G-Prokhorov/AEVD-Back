import os
from flask import Flask, render_template, send_file, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from moviepy.editor import *

UPLOAD_FOLDER = './video'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed

@app.route("/")
def index():
     return "Hello, gey Worlds!"

@app.route("/upload",  methods=["GET", "POST"])
def upload():
     saveFiles = []
     if request.method == 'POST':
          files = request.files.getlist("file")
          audio = request.files['audio']
          mark = request.values['mark']
          start = request.values['time']
          size = request.values['size']
          filterVideo = request.values['filter']

          if audio and allowed_file(audio.filename, ["mp3"]):
               filename = audio.filename.rsplit('.', 1)[1]
               audio.save(os.path.join(app.config['UPLOAD_FOLDER'], "audio." + filename))

          for file in files:
               if file and allowed_file(file.filename, ['mp4', 'webm']):
                    filename = secure_filename(file.filename)
                    saveFiles.append(filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

          videos = []

          for file in saveFiles:
               videoTmp = VideoFileClip(app.config['UPLOAD_FOLDER'] +"/"+ file)
               videos.append({
                    "video": videoTmp,
                    "duration": float(videoTmp.duration),
                    "name": file,
                    "start": 0,
               })
               
          videos.sort(key=lambda k: k["duration"], reverse=True)
          for i in videos:
               print(i["duration"])

          return jsonify(success=True)

     for file in saveFiles:
          os.remove(app.config['UPLOAD_FOLDER'] +"/"+ file)

     return send_file("./video/Aestheticvideo.mp4")
