import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class emailService:
    def __init__(self):
        self.senderEmail = "soccermatchscheduler@gmail.com"
        self.senderName = "Soccer Match Scheduler"
        self.stmp_username = ""
        self.stmp_password = ""
        self.HOST = "email-smtp.us-east-1.amazonaws.com"
        self.PORT = 587

    def createMessage(self, type, receiverEmail, match_details):
        subject = ""
        body = ""

        if type == "generalRequest":  # Team is looking for any match
            subject = "New General Match Request from SoccerMatchScheduler"
            #get the all team name data and show them
            body = f"""<html>
            <head></head>
            <body>
                <h1>{match_details['team1']} is looking for any match</h1>
                <h4>Other Teams Looking for a Match are as Follows:</h4>
                <p>
                    Team Name: {match_details['team1']}<br>
                </p>
                
            </body>
            </html>"""

        elif type == "specialRequest":  # Team wants to play with a specific team
            subject = "New Special Match Request from SoccerMatchScheduler"
            body = f"""<html>
            <head></head>
            <body>
                <h1>{match_details['team1']} wants to match with your team</h1>
                <h4>Match Details are as follows:</h4>
                <p>
                    Date: {match_details['date']}<br>
                    Time: {match_details['time']}<br>
                    Match: {match_details['team1']} vs {match_details['team2']}<br>
                </p>
                
                </p>
            </body>
            </html>"""

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email.utils.formataddr((self.senderName, self.senderEmail))
        msg['To'] = receiverEmail
        part = MIMEText(body, 'html')
        msg.attach(part)
        return msg.as_string()

    def sendMessage(self, type, receiverEmail, match_details):
        """
        Sends the email using the SMTP server.

        Args:
        type (str): Type of match request ('generalRequest' or 'specialRequest').
        receiverEmail (str): Recipient's email address.
        match_details (dict): Dictionary containing match details.
        """
        try:
            server = smtplib.SMTP(self.HOST, self.PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.stmp_username, self.stmp_password)
            server.sendmail(
                self.senderEmail,
                receiverEmail,
                self.createMessage(type, receiverEmail, match_details)
            )
            server.close()
        except Exception as e:
            print("Error: ", e)
        else:
            print("Email sent!")
