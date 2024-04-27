from flask import Flask,jsonify,request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename 
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps

from im_to_txt import get_text_from_image
from MODULE5 import summarize_video
from MODULE1 import summarize_pdf
from ai import send_to_ai
UPLOAD_FOLDER = "modules/uploadedData/"
# DB client 
client = MongoClient('mongodb://localhost:27017/')
history = client['Users']['History']
users = client['Users']['Users']

def save_history(email,data,module,link=""):
    time = datetime.now()
    if(link):
        if (history.find_one_and_update({'email':email,'link':link},{ '$set': { "time" : time,'data':data} })):
            print('history already found (YT), Only updating time :D ')
            return 
    if (history.find_one_and_update({'email':email,'data':data},{ '$set': { "time" : time} })):
        print('history already found , Only updating time :D ')
        return 
    history.insert_one({'email': email, 'data': data ,'link':link,'module':module,'time':time})
    print('history saved Successfulyy ! ')
    return 1
app = Flask(__name__)
CORS(app)
@app.route('/api/summarizetext',methods=['POST']) 
def return_summary():
    text  = request.get_json()['text']
    email = request.get_json()['email']

    summary = send_to_ai(text)
    response = jsonify({"message":summary})
    response.headers.add("Access-Control-Allow-Origin", "*")
    if(email):
        save_history(email,summary,'Text Summarizer','-')

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
        email = request.form.get('email')
        txt = get_text_from_image(os.path.join(UPLOAD_FOLDER, filename))
        if(txt =="0words-found"):
            response =  jsonify({"text":"Error Occured , possibly no words found "})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        txt = txt.split('\n')
        response = jsonify({"text":txt})
        response.headers.add("Access-Control-Allow-Origin", "*")

        if(email and email!="null" ):
            save_history(email=email,data=txt,module='Image To Text',link=filename)
        return response


@app.route('/api/youtubesummarizer',methods=['POST'])
def vids_summary():
    try:
        link = request.get_json()['link']
        email = request.get_json()['email']

        summary = summarize_video(link) 
        response = jsonify({"result":summary})
        response.headers.add("Access-Control-Allow-Origin", "*")
        if(email and email!="null" ):
            save_history(email,summary,'Youtube Summarizer',link)
        return response
    except Exception as e:
        print(f"An error occured {e}")
        return 'error!' , 400

@app.route('/api/pdfsummarizer',methods=['POST']) 
def pdf_summary():
    d = {}
    try:
        file = request.files['pdf']
        email = request.form.get('email')
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
        if(email and email!="null" ):
            save_history(email,txt,'PDF Summarizer',filename)
        return jsonify({"text":txt})

@app.route('/register', methods=['POST'])
def register():
    fullname = request.json['fullname']
    email = request.json['email']
    password = request.json['password']

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

@app.route('/history', methods=['POST'])
def get_history():
    class base_row:
        def __init__(self,email,data,link,module,time) -> None:
            self.email = email
            self.data = data
            self.link = link
            self.module = module
            self.time = time
        def serialize(self):
            return {
                'email': self.email, 
                'data': self.data,
                'link':self.link,
                'module': self.module,
                'time':self.time,
            }
    email = request.get_json()['email']
    elements = history.find({'email':email})
    rows = []
    for element in elements:
        email = element['email']
        data = element['data']
        link = element['link']
        module = element['module']
        time = element['time']
        row =  base_row(email,data,link,module,time)
        rows.append(row)

    response = jsonify(result=[e.serialize() for e in rows])
    print('Links =>> ',response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if( __name__ == "__main__"):
    app.run(debug=True,port=8080)