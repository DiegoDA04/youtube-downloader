from flask import Flask, request, render_template, send_file, jsonify
from pytubefix import YouTube
import os

app = Flask(__name__)
#DOWNLOAD_FOLDER = 'downloads'
#os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form.get('link')
        download_type = request.form.get('download_type')
        quality = request.form.get('quality')
        
        if not link:
            return "Por favor ingresa un enlace válido.", 400
        
        try:
            yt = YouTube(link)
            stream = None
            
            if download_type == 'audio':
                stream = yt.streams.get_audio_only()
                file_path = stream.download(mp3 = True)
            elif download_type == 'video':
                if quality:
                    # Filter by resolution and FPS
                    stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=quality).first()
                else:
                    # Fallback to default if no quality is selected
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
                file_path = stream.download()
            else:
                return "Tipo de descarga no válido.", 400

            if file_path:
                return send_file(file_path, as_attachment=True)
            else:
                return "No se encontró el stream adecuado.", 404
        except Exception as e:
            return str(e), 500

    return render_template('index.html')

@app.route('/qualities', methods=['GET'])
def qualities():
    link = request.args.get('link')
    if not link:
        return jsonify([]), 400
    
    try:
        yt = YouTube(link)
        qualities = []
        for stream in yt.streams.filter(progressive=True, file_extension='mp4'):
            qualities.append({
                'res': stream.resolution,
                'fps': stream.fps
            })
        return jsonify(qualities)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
