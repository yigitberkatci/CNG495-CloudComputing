from flask import Flask, jsonify, request
from db_config import get_db_connection
from hashlib import sha256
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "SoccerMatch Scheduler API is running!"

"""@app.route('/timeslot', methods=['GET'])
def get_timeslot():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  #data as dictionary

        query = "SELECT * FROM TimeSlot"
        cursor.execute(query)
        timeslots = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "data": timeslots}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500"""

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
@app.route("/booking", method=['POST'])
def booking():
    try:
        data = request.get_json()
        team1 = data.get('team1')
        team2 = data.get('team2')
        timeslot = data.get('timeslot')
        type = "Match Invite"

        connection = get_db_connection()
        cursor = connection.cursor()

        if team2 == None:
            msg = f"Team {team1} is looking for opponents!"

            # get ID of team1
            query = "SELECT TeamID FROM Team WHERE Name = %s"
            cursor.execute(query, (team1,))
            team1ID = cursor.fetchone()

            #get timeslot ID
            query = "SELECT TimeSlotID FROM TimeSlot WHERE StartTime = %s"
            cursor.execute(query, (timeslot,))
            timeslotID = cursor.fetchone()

            # insert into notification
            query = "INSERT INTO Notification (SenderID, Message, TimeSlotID, Date, NotificationType) VALUES (%s, %s, %s, %s, %s)"
            values = (team1ID, msg, timeslotID, datetime.now(), type)
        else:
            msg = f"Team {team1} want to play a match for you!"

            # get IDs of teams
            query = "SELECT TeamID FROM Team WHERE Name = %s"
            cursor.execute(query, (team1,))
            team1ID = cursor.fetchone()

            query = "SELECT TeamID FROM Team WHERE Name = %s"
            cursor.execute(query, (team2,))
            team2ID = cursor.fetchone()

            # get timeslot ID
            query = "SELECT TimeSlotID FROM TimeSlot WHERE StartTime = %s"
            cursor.execute(query, (timeslot,))
            timeslotID = cursor.fetchone()

            # insert into notification
            query = "INSERT INTO Notification (SenderID, ReceiverID, TimeSlotID, Message, Date, NotificationType) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (team1ID, team2ID, timeslotID, msg, datetime.now(), type)

        cursor.execute(query, values)
        connection.commit()

        #send an email
        #will be added later on

        return jsonify({"success": True, "message": "Registration successful"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
