import os
from flask import Flask, render_template, send_file, request, jsonify
from flask_cors import CORS
from numpy import insert
from werkzeug.utils import secure_filename
from moviepy.editor import *
import moviepy.video.fx.all as vfx
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

musicFiles = [ {
          "path": "Swag.mp3",
          "artist": "LostGift",
          "title": "Swag",    
          "smile": "cool",
     }, {
        "path": "elyotto_-_sugar_crash.mp3",
        "artist": "Elyotto",
        "title": "Sugar crash",
        "smile": "cool",    
     }, {
          "path": "I Just Want to Be the One You Love.mp3",
          "artist": "Darkohtrash",
          "title": "I Just Want to Be the One You Love",    
          "smile": "sad",
     }, {
          "path": "I Need a Girl.mp3",
          "artist": "Lo-fi Type Beat",
          "title": "I Need a Girl",
          "smile": "sad",    
     }, {
          "path": "Sufjan Stevens - Mystery of Love.mp3",
          "artist": "Sufjan Stevens",
          "title": "Mystery of Love", 
          "smile": "sad",   
     }, {
          "path": "Future - Mask Off (Aesthetic Remix).mp3",
          "artist": "Future",
          "title": "Mask Off (Aesthetic Remix)", 
          "smile": "cool",   
     }, {
          "path": "1570655028_Joji_-_SLOW_DANCING_IN_THE_DARK.mp3",
          "artist": "Joji",
          "title": "SLOW DANCING IN THE DARK", 
          "smile": "sad",   
     }, {
          "path": "eyes blue like the atlantic (slowed+reverb).mp3",
          "artist": "Sista Prod",
          "title": "Eyes blue like the atlantic",
          "smile": "sad",    
     }]

@app.route("/music")
def music():
     response = app.response_class(
          response=json.dumps(musicFiles),
          status=200,
          mimetype='application/json')
     return response

@app.route("/getMusic/<path>")
def getMusic(path=None):
     if path and any(d['path'] == path for d in musicFiles):
          return send_file(os.path.join("./music", path))
     else:
          response = app.response_class(
          status=400)
          return response        


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

          videos = saveFileFunc(audio, files, size)
          
          mark.sort(key=lambda t: t["time"])
          mark.append({"time": 20.0})

          countV = int(len(videos) * 0.75)
          result = []
          curent = 0.0

          for interval in mark:
               time = interval["time"] - curent
               best = None
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
                    clear(filePath)
                    print("ERROR")
                    response = app.response_class(
                    status=400)
                    return response  

               tmp = best["video"].subclip(best["start"], best["start"] + time) 
               result.append(tmp)
               videos.remove(best) # because of memory address
               best["start"] += (time + 5)
               best["duration"] -= (time + 5)
               best["block"] = countV

               insert = False
               for i in range(len(videos)):
                    if best["duration"] < videos[i]["duration"]:
                         videos.insert(i, best)
                         insert = True
                         break

               if not insert:
                    videos.append(best)

               curent = interval["time"]

          if not result:
               clear(filePath)
               response = app.response_class(
               status=400)
               return response  

          audioclip = AudioFileClip(os.path.join(filePath, "audio.mp3")).subclip(start, start + 20)
          final = concatenate_videoclips(result).set_audio(audioclip)
          resultFILE = os.path.join("./result", str(uuid.uuid4()) + ".mp4")

          if filterVideo == "b&w":
               final = vfx.blackwhite(final, RGB=None, preserve_luminosity=True)

          final.write_videofile(resultFILE, fps=25)
          response = app.response_class(
          status=200)
          return response  


     clear(filePath)

     if resultFILE:
          return send_file(resultFILE)
     else:
          response = app.response_class(
          status=200)
          return response  


def clear(filePath):
     if (filePath != ""):
          path = os.path.join(filePath, "audio.mp3")
          if os.path.isfile(path):
               os.remove(path)
          for f in saveFiles:
               path = os.path.join(filePath, f)
               if os.path.isfile(path):
                    os.remove(path)
          
          os.rmdir(filePath)

def saveFileFunc (audio, files, size):
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

     if size == "9:16":
          height = 1280
     else:
          height = 720

     for file in saveFiles:
          videoTmp = VideoFileClip(os.path.join(filePath, file))
          (w, h) = videoTmp.size
          if w >= h:
               videoTmp = videoTmp.resize(height=height)
          else:
               videoTmp = videoTmp.resize(width=720)
          
          (w, h) = videoTmp.size
          cropped_clip = crop(videoTmp, width=720, height=height, x_center=w/2, y_center=h/2)
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
