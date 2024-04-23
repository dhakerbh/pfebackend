from flask import Flask,jsonify,request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename 
from pymongo import MongoClient

from im_to_txt import get_text_from_image
from MODULE5 import summarize_video
from MODULE1 import summarize_pdf
from ai import send_to_ai
UPLOAD_FOLDER = "modules/uploadedData/"

app = Flask(__name__)
CORS(app)
@app.route('/api/summarizetext',methods=['POST']) 
def return_summary():
    text  = request.get_json()['text']
    summary = send_to_ai(text)
    response = jsonify({"message":summary})
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
        response = jsonify({"text":"Error Occured , File not Uploaded "})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    if(d['status']==1):
        txt = get_text_from_image(os.path.join(UPLOAD_FOLDER, filename))
        if(txt =="0words-found"):
            response =  jsonify({"text":"Error Occured , possibly no words found "})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        txt = txt.split('\n')
        response = jsonify({"text":txt})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


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
        return 'error!'

@app.route('/api/pdfsummarizer',methods=['POST']) 
def pdf_summary():
    d = {}
    try:
        file = request.files['pdf']
        filename = secure_filename(file.filename) 
        print(f"Uploading file {filename}")
        file.save(UPLOAD_FOLDER+filename)
        d['status'] = 1
    except Exception as e:
        print(f"Couldn't upload file {e}")
        d['status'] = 0
    if(d['status']==1):
        txt = summarize_pdf(os.path.join(UPLOAD_FOLDER, filename))
        txt = txt.split('\n')
        return jsonify({"text":txt})

@app.route('/register', methods=['POST'])
def register():
    fullname = request.json['fullname']
    email = request.json['email']
    password = request.json['password']
    client = MongoClient('mongodb://localhost:27017/')
    mydb = client['Users']
    users = mydb['Users']

    finding = users.find_one({'email': email})
    if(finding is not None):
        response =  jsonify({'message': 'User Already Exists'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    else:
        users.insert_one({'fullname': fullname, 'email': email, 'password': password})
        response =  jsonify({'message': 'User registered successfully'})
    return response , 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    client = MongoClient('mongodb://localhost:27017/')
    mydb = client['Users']
    users = mydb['Users']

    user = users.find_one({'email': email, 'password': password})

    if(user is not None):
        response =  jsonify({'message': 'Logged in Successfully',"profile":str(user.get('fullname'))[0:2]})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
    else:
        if(users.find_one({"email":email})):
            response = jsonify({"message":"Incorrect Password"})
        else:
            response = jsonify({"message":"User not found !"})
    return response , 400

if( __name__ == "__main__"):
    app.run(debug=True,port=8080)