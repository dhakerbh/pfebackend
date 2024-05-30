from flask import Flask,jsonify,request
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename 
from pymongo import MongoClient
import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import secrets

from im_to_txt import get_text_from_image
from MODULE5 import summarize_video
from MODULE1 import summarize_pdf
from ai import send_to_ai

UPLOAD_FOLDER = "modules/uploadedData/"
# DB client 
client = MongoClient('mongodb://localhost:27017/')
history = client['Users']['History']
users = client['Users']['Users']
tokens = client['Users']['Tokens']


def save_history(email,data,module,link=""):
    time = datetime.datetime.now()
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
app.config['SECRET_KEY'] = 'RA33D'

CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

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
    password=generate_password_hash(password, method='pbkdf2',salt_length=10)
    if(finding is not None):
        response =  jsonify({'message': 'User Already Exists'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400
    else:
        users.insert_one({'fullname': fullname, 'email': email, 'password': password,'role':"user"})
        response =  jsonify({'message': 'User registered successfully'})
    return response , 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    user = users.find_one({'email': email})
    if not user or not check_password_hash(user.get('password'), password) :
        if(user):
            response = jsonify({"message":"Incorrect Password"})
        else:
            response = jsonify({"message":"User not found !"})
    else:
        payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'email': email,
        "profile":str(user.get('fullname'))[0:2],
        "role":str(user.get('role')),
        'id':str(user.get('_id')),
        'iat': datetime.datetime.utcnow().timestamp() 
    }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        response =  jsonify({'message': 'Logged in Successfully',"token":token})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
   
        
    return response , 400
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

@app.route('/history', methods=['POST'])
def get_history():
    class base_row:
        def __init__(self,email,data,link,module,time,id) -> None:
            self.email = email
            self.data = data
            self.link = link
            self.module = module
            self.time = time
            self.id = id
        def serialize(self):
            return {
                'email': self.email, 
                'data': self.data,
                'link':self.link,
                'module': self.module,
                'time':self.time,
                'id':self.id,
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
        id = str(element['_id'])
        row =  base_row(email,data,link,module,time,id)
        rows.append(row)

    response = jsonify(result=[e.serialize() for e in rows])
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/deletehistory',methods=['POST'])
def delete():
    id = request.get_json()['id']
    email = request.get_json()['email']
    print('id : ', id , 'email : ' , email)
    if(history.find_one_and_delete({'_id':ObjectId(id),'email':email})):
        print('Deleted  !! ')
    else:
        print('Damn -_--')
        return 400
    return jsonify({'hello':'hello'})


@app.route('/users',methods=['GET'])
def get_users():
    class base_row:
        def __init__(self,id,email,fullname,password,role) -> None:
            self.email = email
            self.fullname = fullname
            self.password = password
            self.role = role
            self.id = id
        def serialize(self):
            return {
                'email': self.email, 
                'fullname': self.fullname,
                'password':self.password,
                'role': self.role,
                'id':self.id,
            }
    users_list = users.find()
    rows = []
    for element in users_list:
        email = element['email']
        fullname = element['fullname']
        password = element['password']
        role = element['role']
        id = str(element['_id'])
        row =  base_row(id,email,fullname,password,role)
        rows.append(row)
    response = jsonify(result=[e.serialize() for e in rows])
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
@app.route('/getEmail', methods=['POST'])
def get_email():
    id = request.get_json()['id']
    email = users.find_one({'_id':ObjectId(id)}).get('email')
    response = jsonify({"email":str(email)})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/adminhistory', methods=['POST'])
def get_admin_history():
    class base_row:
        def __init__(self,email,data,link,module,time,id) -> None:
            self.email = email
            self.data = data
            self.link = link
            self.module = module
            self.time = time
            self.id = id
        def serialize(self):
            return {
                'email': self.email, 
                'data': self.data,
                'link':self.link,
                'module': self.module,
                'time':self.time,
                'id':self.id,
            }
    id = request.get_json()['id']
    email = users.find_one({'_id':ObjectId(id)}).get('email')

    elements = history.find({'email':email})
    rows = []
    for element in elements:
        email = element['email']
        data = element['data']
        link = element['link']
        module = element['module']
        time = element['time']
        id = str(element['_id'])
        row =  base_row(email,data,link,module,time,id)
        rows.append(row)

    response = jsonify(result=[e.serialize() for e in rows])
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/user',methods=['POST'])
def get_user():
    id = request.get_json()['id']
    user = users.find_one({'_id':ObjectId(id)})
    response = jsonify({"id":id,"fullname":user.get('fullname'),"email":user.get('email'),"role":user.get('role'),"isActivated":user.get('isActivated')})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
@app.route('/edituser',methods=['PUT'])
def edit_user():
    received = request.get_json()  
    id = received['id']
    print(received)
    try:
        users.find_one_and_update({'_id':ObjectId(id)},{ '$set':{"fullname" : received['fullname'],"email" : received['email'],"isActivated" : received['isActivated'],"role" : received['role'],} })
        response = jsonify({"message":"success"})
    except:
        response = jsonify({'message':"error"})

    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/resetrequest',methods=['POST'])
def reset_request():
    email = request.get_json()['email']
    found = tokens.find_one({"email":email})
    if(users.find_one({"email":email})):
        if(not found):
            reset_token=secrets.token_urlsafe(32)
            tokens.insert_one({"email":email,"token":reset_token})
        else:
            reset_token = found.get('token')
        #send reset_email
        response = jsonify({"reset":"link sent successfully"})  
    else:
        response = jsonify({"reset":"email address not found!"})  
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
@app.route('/verifyreset',methods=['POST'])
def verify_token():
    token = request.get_json()['token']
    found = tokens.find_one({"token":token})
    if(found):
        response = jsonify({"verify":"verified successfully"}) 
    else:
        response = jsonify({"verify":"Not verified"}),415 
    #send reset_email
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
"""
STILL WORKING ON IT CHANGE PASSWORD!!


"""
@app.route('/changepassword',methods=['PUT'])
def change_password():
    token = request.get_json()['token']
    found = tokens.find_one({"token":token})
    if(found):
        response = jsonify({"verify":"verified successfully"}) 
    else:
        response = jsonify({"verify":"Not verified"}),415 
    #send reset_email
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
if( __name__ == "__main__"):
    app.run(debug=True,port=8080)
    print(generate_password_hash())