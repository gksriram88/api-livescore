from flask import Blueprint, render_template,make_response

audio_page = Blueprint('audio_page', __name__, template_folder='templates')
@audio_page.route('/audio')
def audioHTML():
    return render_template('audio.html')

video_page = Blueprint('video_page', __name__, template_folder='templates')
@video_page.route('/video')
def videoHTML():
    return render_template('video.html')