from moviepy.editor import *
from moviepy.video.fx.all import crop
from numpy.lib.function_base import insert
from werkzeug.utils import secure_filename

mark = [
{"id": 1621031659566.6, "time": 2.6, "left": 117.17},
{"id": 1621031659568.9, "time": 4.9, "left": 221.705},
{"id": 1621031659570.3, "time": 6.300000000000001, "left": 285.33500000000004},
{"id": 1621031659572.6, "time": 8.600000000000001, "left": 389.87000000000006},
{"id": 1621031659574.3, "time": 10.3, "left": 467.13500000000005},
{"id": 1621031659577.2, "time": 13.200000000000001, "left": 598.94},
{"id": 1621031659579, "time": 15.000000000000002, "left": 680.7500000000001},
{"id": 1621031659581.8, "time": 17.8, "left": 808.01}
]
start = 15
size = "1:1"
filterVideo = "bw"

videos = []
for file in ["1.mp4", "2.mp4", "3.mp4", "4.mp4", "5.mp4"]:
    videoTmp = VideoFileClip("./video/" + file).resize(width=720)
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
mark.sort(key=lambda t: t["time"])
mark.append({"time": 20.0})

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
        print("pizdec")
        quit()

    tmp = best["video"].subclip(best["start"], best["start"] + time) 
    videos.remove(best) # because of memory address
    best["start"] += (time + 1)
    best["duration"] -= (time + 1)
    best["block"] = 4
    videos.append(best)

    result.append(tmp)
    curent = interval["time"]

audioclip = AudioFileClip("./video/audio2.mp3").subclip(start, start + 20)
final = concatenate_videoclips(result).set_audio(audioclip)
final.write_videofile("result.mp4", fps=25)


       