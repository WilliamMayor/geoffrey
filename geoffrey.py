import subprocess
import re
import smtplib
import datetime
import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
app = Flask(__name__)

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'scripts')

def pullupdate(repo):
    try:
        if not re.match('\w+', repo):
            return 1, "Invalid repo name: %s" % repo
        script = os.path.join(SCRIPT_DIR,'%s.sh' % repo)
        process = subprocess.Popen(script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = process.communicate()
        return process.returncode, "Output:\n%s\nErrors:\n%s\n" % (output, errors)
    except Exception as e:
        return 1, "Can't call script: %s" % e

def email_details(email_to, repo, exit_status, message):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    GMAIL_LOGIN = 'geoffreyintegration@gmail.com'
    GMAIL_PASSWORD = '#xVciMYMu1'
    TO = email_to
    SUBJECT = "Geoffrey Report"
    MESSAGE = "\n".join([
        "Latest %s Report" % repo,
        "Sent: %s" % datetime.datetime.now(),
        "Exit code: %d" % exit_status,
        "Messages:",
        message
    ])
    BODY = "\r\n".join(["From: %s" % GMAIL_LOGIN,
                       "To: %s" % TO,
                       "Subject: %s" % SUBJECT ,
                       "",
                       MESSAGE])
        
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(GMAIL_LOGIN, GMAIL_PASSWORD)
    server.sendmail(GMAIL_LOGIN, [TO], BODY)
    server.close()

@app.route('/', methods=['POST'])
def post():
    try:
        repo = request.args['repo']
    except Exception as e:
        return "No repo: %s" % e
    exit_status, message = pullupdate(repo)
    try:
        email = request.args['email']
        email_details(email, repo, exit_status, message)
    except KeyError:
        pass
    if exit_status == 0:
        return "Success: %s" % message
    else:
        return "Failure: %s" % message

@app.route('/', methods=['GET'])
def get():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)