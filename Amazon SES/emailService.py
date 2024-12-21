import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class emailService:
    def __init__(self):
        self.senderEmail = "soccermatchscheduler@gmail.com"
        self.senderName = "Soccer Match Scheduler"
        self.stmp_username = "will be added later on"
        self.stmp_password = "will be added later on"
        self.HOST = "email-smtp.us-east-1.amazonaws.com"
        self.PORT = 587
    def createMessage(self,type,receiverEmail):
        subject = ""
        body = ""
        if type == "generalRequest":  # team is looking for any match
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
        elif type == "specialRequest":  # team wants to play with special team
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
        msg['From'] = email.utils.formataddr((self.senderName, self.senderEmail))
        msg['To'] = receiverEmail
        part = MIMEText(body, 'html')
        msg.attach(part)
        return msg.as_string()
    def sendMessage(self,type,receiverEmail):
        try:
            server = smtplib.SMTP(self.HOST, self.PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.stmp_username, self.stmp_password)
            server.sendmail(self.senderEmail, receiverEmail, self.createMessage(type, receiverEmail))
            server.close()
        except Exception as e:
            print("Error: ", e)
        else:
            print("Email sent!")

if __name__ == "__main__":
    service = emailService()
    type = "specialRequest"
    receiverEmail = "example@metu.edu.tr"
    service.sendMessage(type,receiverEmail)