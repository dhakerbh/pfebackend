from flask import Flask,jsonify,request
from flask_cors import CORS
from io import BytesIO
import os
from werkzeug.utils import secure_filename 

from im_to_txt import get_text_from_image
from MODULE5 import summarize_video
UPLOAD_FOLDER = "uploadedData/"

app = Flask(__name__)
CORS(app)
@app.route('/api/summarizetext',methods=['POST']) 
def return_summary():
    summary2  = request.get_json()['text']
    response = jsonify({"message":summary2})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
CORS(app)

@app.route('/api/imtotxt',methods=['POST']) 
def return_imextracted():
    d = {}
    try:
        file = request.files['image']
        filename = secure_filename(file.filename) 
        print(f"Uploading file {filename}")
        file.save(UPLOAD_FOLDER+filename)
        d['status'] = 1
    except Exception as e:
        print(f"Couldn't upload file {e}")
        d['status'] = 0
    if(d['status']==1):
        txt = get_text_from_image(os.path.join(UPLOAD_FOLDER, filename))
        txt = txt.split('\n')
        return jsonify({"text":txt})


@app.route('/api/youtubesummarizer',methods=['POST'])
def vids_summary():
    try:
        link = request.get_json()['link']
        summary = summarize_video(link) 
        response = jsonify({"result":summary})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as e:
        print(f"An error occured {e}")



if( __name__ == "__main__"):
    app.run(debug=True,port=8080)