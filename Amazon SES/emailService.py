import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender = "soccermatchscheduler@gmail.com"
senderName = "Soccer Match Scheduler"

receiver = "kutay.oren@metu.edu.tr"

stmp_username = "AKIA2LIP2CXYVA5GFXXT"
stmp_password = "BBhTWoAuwxVDGI8jOEPz055teLhEV/YhyNw71TUs2tIT"

# config_set = "ConfigSet"
HOST = "email-smtp.eu-north-1.amazonaws.com"
PORT = 587

subject = "New match request from SoccerMatchScheduler"

body = """<html>
<head></head>
<body>
    <h1>New Match Request from 'teamname'</h1>
    <h4>Match Details are following</h4>
    <p>Date: 'Date'<br>
       Time: 'time'<br>
       Match: 'team1-team2'<br>
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
try:
    server = smtplib.SMTP(HOST, PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(stmp_username, stmp_password)
    server.sendmail(sender, receiver, msg.as_string())
    server.close()
except Exception as e:
    print("Error: ", e)
else:
    print("Email sent!")
