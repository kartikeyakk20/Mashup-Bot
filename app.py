from flask import Flask, render_template,request
from youtube_channel_videos_scraper_bot import *
import youtube_dl 
import glob 
from pydub import AudioSegment
import zipfile
from youtubesearchpython import VideosSearch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydub import AudioSegment
import moviepy.editor as mp

app=Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

def main(channel_name,no_of_videos,trim_time,email):
    no_of_videos=int(no_of_videos)
    trim_time=int(trim_time)
    videosSearch = VideosSearch(channel_name, limit = no_of_videos)
    urls=[]
    for i in range(0,no_of_videos):
        urls.append(videosSearch.result()["result"][i]["link"])
        download_audio(urls[i])
    mp3s = glob.glob('./*.mp3')
    for i in range(0,no_of_videos):
        audio = mp3s[i]
        trimfile(audio, 0, trim_time,i)
    sound1=AudioSegment.from_mp3("./audio0.mp3")
    for i in range(1,no_of_videos):
        audio_file="./audio"+ str(i)+".mp3"
        sound2=AudioSegment.from_mp3(audio_file)
        sound1=sound1.append(sound2)
    sound1.export("./final.mp3",format="mp3")
    zip = zipfile.ZipFile("102003648.zip", "w", zipfile.ZIP_DEFLATED)
    zip.write("./final.mp3")
    zip.close()
    fromaddr = "Enter Your Email ID."
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Mashup Assignment"
    filename = "102003648.zip"
    attachment = open("./102003648.zip", "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, "Enter your password")
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

@app.route("/",methods=['POST'])
def home():
    channel_name=request.form['singername']
    no_of_videos=request.form['no_of_videos']
    trim_time=request.form['timestamp']
    email=request.form['email']
    main(channel_name,no_of_videos,trim_time,email)
    return "<h1><center>File Processed.</center></h1>"

def download_audio(yt_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])
def trimfile(audio_file, start, end,i):
    audio = mp.AudioFileClip("./"+audio_file)
    audio_cut = audio.subclip(start, end)
    audio_cut.write_audiofile("audio"+ str(i)+".mp3")

if __name__=="__main__":
    app.run(debug=True)