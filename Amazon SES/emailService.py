import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender = "soccermatchscheduler@gmail.com"
senderName = "Soccer Match Scheduler"

receiver = "yigit.atci@metu.edu.tr"

stmp_username = "AKIA2LIP2CXYRIDDP3GR"
stmp_password = "BNI2yYARpobiqTz+wDg15R1FeZKQVF4X2zcyJOBYPSLa"

# config_set = "ConfigSet"
HOST = "email-smtp.us-east-1.amazonaws.com"
PORT = 587
def createMessage(type):
    subject = ""
    body = ""
    if type == "generalRequest": #team is looking for any match
        subject = "New General Match Request from SoccerMatchScheduler"
        body = """<html>
        <head></head>
        <body>
            <h1>'teamname' is looking for any match</h1>
            <h4>Match Details are following</h4>
            <p>Date: 'Date'<br>
               Time: 'time'<br>
               Publishing Team Name: 'teamname'<br>
            </p>
            <p>To respond to the match request, please go to:<br>
            <a href = 'http://www.soccermatchscheduler.com.s3-website.eu-north-1.amazonaws.com'>SoccerMatchScheduler</a>
        
        
        </body>
        </html>"""
    elif type == "specialRequest": #team wants to play with special team
        subject = "New Special Match Request from SoccerMatchScheduler"
        body = """<html>
                <head></head>
                <body>
                    <h1>'teamname' wants to match with your team</h1>
                    <h4>Match Details are following</h4>
                    <p>Date: 'Date'<br>
                       Time: 'time'<br>
                       Match:'team1 - team2'<br>
                    </p>
                    <p>To respond to the match request, please go to:<br>
                    <a href = 'http://www.soccermatchscheduler.com.s3-website.eu-north-1.amazonaws.com'>SoccerMatchScheduler</a>


                </body>
                </html>"""


    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr((senderName, sender))
    msg['To'] = receiver
    # http://www.soccermatchscheduler.com.s3-website.eu-north-1.amazonaws.com
    part = MIMEText(body, 'html')
    msg.attach(part)
    return msg.as_string()

try:
    server = smtplib.SMTP(HOST, PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(stmp_username, stmp_password)
    server.sendmail(sender, receiver, createMessage("specialRequest"))
    server.close()
except Exception as e:
    print("Error: ", e)
else:
    print("Email sent!")
