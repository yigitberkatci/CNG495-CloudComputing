from flask import Flask, jsonify, request
from db_config import get_db_connection
from hashlib import sha256
from flask_cors import CORS
from datetime import datetime
from AmazonSES.emailService import emailService

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "SoccerMatch Scheduler API is running!"

@app.route('/timeslot', methods=['GET'])
def get_timeslot():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  #data as dictionary

        query = """
                SELECT 
                    ts.TimeSlotID,
                    ts.StartTime,
                    ts.EndTime,
                    ts.IsBooked,
                    ts.MatchID,
                    t1.Name AS Team1Name,
                    t2.Name AS Team2Name
                FROM TimeSlot ts
                LEFT JOIN SoccerMatch sm ON ts.MatchID = sm.MatchID
                LEFT JOIN Team t1 ON sm.Team1ID = t1.TeamID
                LEFT JOIN Team t2 ON sm.Team2ID = t2.TeamID
                WHERE ts.IsBooked = TRUE
                ORDER BY ts.StartTime;
                """
        cursor.execute(query)
        timeslots = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "data": timeslots}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT Password FROM Team WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if not user:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        #hashing using SHA256
        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        #password verify
        if hashed_password != user['Password']:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        return jsonify({"success": True, "message": "Login successful"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        team_name = data.get('team_name')
        email = data.get('email')
        password = data.get('password')

        if not team_name or not email or not password:
            return jsonify({"success": False, "message": "Team name, email, and password are required"}), 400

        #hash with SHA256
        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM Team WHERE Email = %s"
        cursor.execute(query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"success": False, "message": "Email already exists"}), 409

        query = "INSERT INTO Team (Name, Email, Password) VALUES (%s, %s, %s)"
        cursor.execute(query, (team_name, email, hashed_password))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Registration successful"}), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
@app.route("/booking", methods=['POST'])
def booking():
    service = emailService()
    try:
        data = request.get_json()
        team1 = data.get('team1')
        team2 = data.get('team2')
        timeslot = data.get('timeslot')

        match_details = {
            "date": datetime.now(),
            "time": datetime.now().time(),
            "team1": team1,
            "team2": team2  # Optional for generalRequest
        }

        connection = get_db_connection()
        cursor = connection.cursor()

        if team2 is None:  # General request
            type = "generalRequest"
            msg = f"Team {team1} is looking for opponents!"

            # Get ID of team1
            query = "SELECT TeamID FROM Team WHERE Name = %s"
            cursor.execute(query, (team1,))
            team1ID = cursor.fetchone()
            if team1ID:
                team1ID = team1ID[0]  # Extract value from tuple
            else:
                return jsonify({"success": False, "error": "Team1 not found"}), 400

            # Get TimeSlot ID
            query = "SELECT TimeSlotID FROM TimeSlot WHERE StartTime = %s"
            cursor.execute(query, (timeslot,))
            timeslotID = cursor.fetchone()
            if timeslotID:
                timeslotID = timeslotID[0]  # Extract value from tuple
            else:
                return jsonify({"success": False, "error": "Timeslot not found"}), 400

            # Get all email addresses
            query2 = "SELECT Email FROM Team"
            cursor.execute(query2)
            receiverEmails = [email[0] for email in cursor.fetchall()]  # Extract emails as a list

            # Send the email to all teams
            for receiverEmail in receiverEmails:
                service.sendMessage(type, receiverEmail, match_details)

            # Insert into Notification table
            query = "INSERT INTO Notification (SenderID, Message, TimeSlotID, Date, NotificationType) VALUES (%s, %s, %s, %s, %s)"
            values = (team1ID, msg, timeslotID, datetime.now(), type)

        else:  # Special request
            type = "specialRequest"
            msg = f"Team {team1} wants to play a match with your team!"

            # Get IDs of both teams
            query = "SELECT TeamID FROM Team WHERE Name = %s"
            cursor.execute(query, (team1,))
            team1ID = cursor.fetchone()
            if team1ID:
                team1ID = team1ID[0]  # Extract value from tuple
            else:
                return jsonify({"success": False, "error": "Team1 not found"}), 400

            cursor.execute(query, (team2,))
            team2ID = cursor.fetchone()
            if team2ID:
                team2ID = team2ID[0]  # Extract value from tuple
            else:
                return jsonify({"success": False, "error": "Team2 not found"}), 400

            # Get TimeSlot ID
            query = "SELECT TimeSlotID FROM TimeSlot WHERE StartTime = %s"
            cursor.execute(query, (timeslot,))
            timeslotID = cursor.fetchone()
            if timeslotID:
                timeslotID = timeslotID[0]  # Extract value from tuple
            else:
                return jsonify({"success": False, "error": "Timeslot not found"}), 400

            # Get email of team2
            query = "SELECT Email FROM Team WHERE Name = %s"
            cursor.execute(query, (team2,))
            receiverEmail = cursor.fetchone()
            if receiverEmail:
                receiverEmail = receiverEmail[0]  # Extract email value
            else:
                return jsonify({"success": False, "error": "Receiver email not found"}), 400

            # Send the email to the specific team
            service.sendMessage(type, receiverEmail, match_details)

            # Insert into Notification table
            query = "INSERT INTO Notification (SenderID, ReceiverID, TimeSlotID, Message, Date, NotificationType) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (team1ID, team2ID, timeslotID, msg, datetime.now(), type)

        # Execute the final insert query
        cursor.execute(query, values)
        connection.commit()

        return jsonify({"success": True, "message": "Booking successful"}), 201

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

@app.route('/api/teams-asking-for-match', methods=['GET'])
def get_teams_asking_for_match():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT Name FROM Team WHERE isAskingForMatch = TRUE"
        cursor.execute(query)
        teams = cursor.fetchall()
        cursor.close
        connection.close

        return jsonify({"success": True, "data": teams}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
