from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail,Message

load_dotenv()
app = Flask(__name__)


mail = Mail(app)
def send_email(recipient, subject,  html_body):
    msg = Message(subject, sender="your_name <your_gmail_address>", recipients=[recipient])
    msg.html = html_body
    mail.send(msg)
def get_verify_template(token):
    verify_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <style type="text/css">
        span {
            font-weight: 600;
            font-size: 15px;
        }
        </style>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
    <body>
        <p>
        Happy to have you on our website: Click
        <a href="http://localhost:3000/verify/"""+token+"""\">Here</a> to confirm your
        registration.
        </p>
        <span>SS Team ©</span>
    </body>
    </html>
    """
    return verify_template
def get_change_pass_template(token):
    pass_template = """
    <!DOCTYPE html>
<html lang="en">
  <head>
    <style type="text/css">
      span {
        font-weight: 600;
        font-size: 15px;
      }
    </style>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  </head>
  <body>
    <p>
      A password reset request has been made by your email, Click Here
      <a href="http://localhost:3000/reset/"""+token+"""\">Here</a> to proceed with the reset
      process.
    </p>
    <span>SS Team ©</span>
  </body>
</html>
    """
    return pass_template