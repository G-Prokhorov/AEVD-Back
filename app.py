import os
from flask import Flask, render_template, send_file, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from moviepy.editor import *
from moviepy.video.fx.all import crop
import json
import uuid

app = Flask(__name__)
CORS(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed

@app.route("/")
def index():
     return render_template("index.html")



filePath = ""
resultFILE = ""     
saveFiles = []

@app.route("/upload",  methods=["GET", "POST"])
def upload():
     global filePath
     global resultFILE  
     global saveFiles

     if request.method == 'POST':
          files = request.files.getlist("file")
          audio = request.files['audio']
          mark = json.loads(request.values['mark'])
          start = int(request.values['time'])
          size = request.values['size']
          filterVideo = request.values['filter']

          filePath =  os.path.join("./video/", str(uuid.uuid4()))
          os.mkdir(filePath)

          videos = saveFileFunc(audio, files)
          
          mark.sort(key=lambda t: t["time"])
          mark.append({"time": 20.0})

          result = []

          countV = len(videos)
          result = []
          curent = 0.0

          for interval in mark:
               time = interval["time"] - curent
               for video in videos:
                    if video["block"] != 0:
                         video["block"] -= 1

               for video in videos: # search video
                    #############
                    if video["duration"] >= time and video["block"] == 0:
                         best = video
                         break
                    #############
                    
               if not best:
                    return jsonify(succes=False)

               tmp = best["video"].subclip(best["start"], best["start"] + time) 
               videos.remove(best) # because of memory address
               best["start"] += (time + 5)
               best["duration"] -= (time + 5)
               best["block"] = countV - int(countV / 5)
               videos.append(best)

               result.append(tmp)
               curent = interval["time"]

          if not result:
               return jsonify(success=False)

          audioclip = AudioFileClip(os.path.join(filePath, "audio.mp3")).subclip(start, start + 20)
          final = concatenate_videoclips(result).set_audio(audioclip)
          resultFILE = os.path.join("./result", str(uuid.uuid4()) + ".mp4")
          final.write_videofile(resultFILE, fps=25)
          return jsonify(success=True)


     if (filePath != ""):
          os.remove(os.path.join(filePath, "audio.mp3"))
          for f in saveFiles:
               path = os.path.join(filePath, f)
               if os.path.isfile(path):
                    os.remove(path)
          
          os.rmdir(filePath)

     if resultFILE:
          return send_file(resultFILE)
     else:
          return jsonify(succes=False)


def saveFileFunc (audio, files):
     global filePath
     global saveFiles

     if audio and allowed_file(audio.filename, ["mp3"]):
          filename = audio.filename.rsplit('.', 1)[1]
          audio.save(os.path.join(filePath, "audio." + filename))

     for file in files:
          if file and allowed_file(file.filename, ['mp4', 'webm']):
               filename = secure_filename(file.filename)
               saveFiles.append(filename)
               file.save(os.path.join(filePath, filename))

     videos = []
     for file in saveFiles:
          videoTmp = VideoFileClip(os.path.join(filePath, file))
          (w, h) = videoTmp.size
          if w > h:
               videoTmp = videoTmp.resize(height=720)
          else:
               videoTmp = videoTmp.resize(width=720)
          
          (w, h) = videoTmp.size
          cropped_clip = crop(videoTmp, width=720, height=720, x_center=w/2, y_center=h/2)
          videos.append({
               "video": cropped_clip,
               "duration": float(cropped_clip.duration),
               "name": file,
               "start": 0,
               "block": 0,
          });

     videos.sort(key=lambda k: k["duration"], reverse=True)
     return videos


app.run()
