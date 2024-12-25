from flask import Flask, jsonify, request, session
from db_config import get_db_connection
from hashlib import sha256
from flask_cors import CORS
from datetime import datetime
from AmazonSES.emailService import emailService

#Session configuration
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
                    TIME_FORMAT(ts.StartTime, '%H:%i:%s') AS StartTime,
                    TIME_FORMAT(ts.EndTime, '%H:%i:%s') AS EndTime,
                    ts.IsBooked,
                    t1.Name AS Team1Name,
                    t2.Name AS Team2Name
                FROM TimeSlot ts
                LEFT JOIN SoccerMatch sm ON ts.MatchID = sm.MatchID
                LEFT JOIN Team t1 ON sm.Team1ID = t1.TeamID
                LEFT JOIN Team t2 ON sm.Team2ID = t2.TeamID
                WHERE ts.Date = CURDATE() -- Only for today's date
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
        print(f"Error occurred: {e}")
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

@app.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT 
            t.Name AS Club,
            COUNT(sm.MatchID) AS Played,
            SUM(CASE WHEN sm.Score1 > sm.Score2 AND sm.Team1ID = t.TeamID THEN 1
                     WHEN sm.Score2 > sm.Score1 AND sm.Team2ID = t.TeamID THEN 1
                     ELSE 0 END) AS Won,
            SUM(CASE WHEN sm.Score1 < sm.Score2 AND sm.Team1ID = t.TeamID THEN 1
                     WHEN sm.Score2 < sm.Score1 AND sm.Team2ID = t.TeamID THEN 1
                     ELSE 0 END) AS Lost,
            SUM(CASE WHEN sm.Score1 = sm.Score2 THEN 1 ELSE 0 END) AS Drawn,
            SUM(CASE WHEN sm.Team1ID = t.TeamID THEN sm.Score1
                     WHEN sm.Team2ID = t.TeamID THEN sm.Score2
                     ELSE 0 END) AS GF, -- Goals For
            SUM(CASE WHEN sm.Team1ID = t.TeamID THEN sm.Score2
                     WHEN sm.Team2ID = t.TeamID THEN sm.Score1
                     ELSE 0 END) AS GA, -- Goals Against
            CONCAT(ROUND(
                SUM(CASE WHEN sm.Score1 > sm.Score2 AND sm.Team1ID = t.TeamID THEN 1
                         WHEN sm.Score2 > sm.Score1 AND sm.Team2ID = t.TeamID THEN 1
                         ELSE 0 END) * 100.0 / COUNT(sm.MatchID), 2), '%') AS `Win %`
        FROM Team t
        LEFT JOIN SoccerMatch sm
        ON t.TeamID = sm.Team1ID OR t.TeamID = sm.Team2ID
        GROUP BY t.TeamID
        ORDER BY Played DESC, `Win %` DESC;
        """
        cursor.execute(query)
        rankings = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "data": rankings}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
@app.route("/booking", methods=['POST'])
def booking():
    service = emailService()
    try:
        data = request.get_json()
        team1email = data.get('team1')
        team2 = data.get('team2')
        timeslot = data.get('timeslot')
        start_time, end_time = [time.strip() for time in timeslot.split('-')]

        now = datetime.now()

        # Format the date and time
        date = now.strftime("%Y-%m-%d")  # Only the date

        connection = get_db_connection()
        cursor = connection.cursor()

        # Get team name of logged in team
        query = "SELECT TeamID, Name FROM Team WHERE Email = %s"
        cursor.execute(query, (team1email,))
        result = cursor.fetchone()
        if result:
            team1ID = result[0]
            team1 = result[1]
        else:
            return jsonify({"success": False, "error": "Team1 not found"}), 400

        match_details = {
            "date": date,
            "time": timeslot,
            "team1": team1,
            "team2": team2  # Optional for generalRequest
        }

        connection = get_db_connection()
        cursor = connection.cursor()

        type = "specialRequest"
        msg = f"Team {team1} wants to play a match with your team!"

        # Get ID of second team

        query = "SELECT TeamID FROM Team WHERE Name = %s"
        cursor.execute(query, (team2,))
        team2ID = cursor.fetchone()
        if team2ID:
            team2ID = team2ID[0]  # Extract value from tuple
        else:
            return jsonify({"success": False, "error": "Team2 not found"}), 400

        # Get TimeSlot ID
        query = "SELECT TimeSlotID FROM TimeSlot WHERE StartTime = %s"
        cursor.execute(query, (start_time,))
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

        # Insert into Match table
        query = "INSERT INTO SoccerMatch (Team1ID, Team2ID, Score1, Score2) VALUES (%s, %s, 0, 0)"
        cursor.execute(query, (team1ID, team2ID))
        lastmatchID = cursor.lastrowid

        # Update timeSlot Table
        query = "UPDATE TimeSlot SET IsBooked = TRUE, MatchID = %s WHERE TimeSlotID = %s"
        cursor.execute(query, (lastmatchID, timeslotID))

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

@app.route('/looking-opponents', methods=['POST'])
def looking_opponents():
    try:
        data = request.get_json()
        team = data['team']

        match_details ={
            "team": team
        }
        service = emailService()
        connection = get_db_connection()
        cursor = connection.cursor()

        type = "generalRequest"
        msg = f"Team {team} is looking for opponents!"

        # Get ID of team1
        query = "SELECT TeamID FROM Team WHERE Name = %s"
        cursor.execute(query, (team,))
        team1ID = cursor.fetchone()
        if team1ID:
            team1ID = team1ID[0]  # Extract value from tuple
        else:
            return jsonify({"success": False, "error": "Team1 not found"}), 400


        # Get all email addresses
        query2 = "SELECT Email FROM Team"
        cursor.execute(query2)
        receiverEmails = [email[0] for email in cursor.fetchall()]  # Extract emails as a list

        # Send the email to all teams
        for receiverEmail in receiverEmails:
            service.sendMessage(type, receiverEmail, match_details)

        # Insert into Notification table
        query = "INSERT INTO Notification (SenderID, Message, Date, NotificationType) VALUES (%s, %s, %s, %s)"
        values = (team1ID, msg, datetime.now(), type)

        cursor.execute(query, values)
        connection.commit()

        return jsonify({"success": True, "message": "Looking for opponents successful"}), 201

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/teams-asking-for-match', methods=['GET'])
def get_teams_asking_for_match():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT Name FROM Team WHERE isAskingForMatch = TRUE"
        cursor.execute(query)
        teams = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "data": teams}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/ask-for-match', methods=['POST'])
def ask_for_match():
    try:
        # Get the email from the request data
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        service = emailService()

        # Get ID of team1
        query = "SELECT TeamID, Name FROM Team WHERE Email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            team1ID = result[0]
            team = result[1]
        else:
            return jsonify({"success": False, "error": "Team1 not found"}), 400

        match_details = {
            "team": team
        }

        type = "generalRequest"
        msg = f"Team {team} is looking for opponents!"


        # Get all email addresses
        query2 = "SELECT Email FROM Team"
        cursor.execute(query2)
        receiverEmails = [emails[0] for emails in cursor.fetchall()]  # Extract emails as a list

        # Send the email to all teams
        for receiverEmail in receiverEmails:
            service.sendMessage(type, receiverEmail, match_details)

        # Insert into Notification table
        query = "INSERT INTO Notification (SenderID, Message, Date, NotificationType) VALUES (%s, %s, %s, %s)"
        values = (team1ID, msg, datetime.now(), type)

        cursor.execute(query, values)

        # Update the isAskingForMatch value to TRUE for the team with the given email
        query = "UPDATE Team SET isAskingForMatch = TRUE WHERE Email = %s"
        cursor.execute(query, (email,))

        # Check if any rows were updated
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Team not found"}), 404

        # Commit the changes
        connection.commit()

        return jsonify({"success": True, "message": "Team is now asking for a match"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        # Ensure resources are released
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/stop-asking-for-match', methods=['POST'])
def stop_asking_for_match():
    try:
        # Get the email from the request data
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400

        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Update the isAskingForMatch value to FALSE for the team with the given email
        query = "UPDATE Team SET isAskingForMatch = FALSE WHERE Email = %s"
        cursor.execute(query, (email,))

        # Check if any rows were updated
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Team not found"}), 404

        # Commit the changes
        connection.commit()

        return jsonify({"success": True, "message": "Team is no longer asking for a match"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        # Ensure resources are released
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

#Admin Panel
# 1. Load Teams
@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT TeamID, Name, Email FROM Team"
        cursor.execute(query)
        teams = cursor.fetchall()

        return jsonify({"success": True, "data": teams}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 2. Delete a Team
@app.route('/api/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "DELETE FROM Team WHERE TeamID = %s"
        cursor.execute(query, (team_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Team not found"}), 404

        return jsonify({"success": True, "message": "Team deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 3. Edit a Team
@app.route('/api/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return jsonify({"success": False, "message": "Name and email are required"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "UPDATE Team SET Name = %s, Email = %s WHERE TeamID = %s"
        cursor.execute(query, (name, email, team_id))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Team not found"}), 404

        return jsonify({"success": True, "message": "Team updated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 4. Load Match Scores
@app.route('/api/matches', methods=['GET'])
def get_matches():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT 
                sm.MatchID,
                t1.Name AS Team1Name,
                t2.Name AS Team2Name,
                sm.Score1,
                sm.Score2
            FROM SoccerMatch sm
            JOIN Team t1 ON sm.Team1ID = t1.TeamID
            JOIN Team t2 ON sm.Team2ID = t2.TeamID
        """
        cursor.execute(query)
        matches = cursor.fetchall()

        return jsonify({"success": True, "data": matches}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 5. Update Match Scores
@app.route('/api/matches/<int:match_id>', methods=['PUT'])
def update_match_score(match_id):
    try:
        data = request.get_json()
        score1 = data.get('score1')
        score2 = data.get('score2')

        if score1 is None or score2 is None:
            return jsonify({"success": False, "message": "Both scores are required"}), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        query = "UPDATE SoccerMatch SET Score1 = %s, Score2 = %s WHERE MatchID = %s"
        cursor.execute(query, (score1, score2, match_id))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Match not found"}), 404

        return jsonify({"success": True, "message": "Scores updated successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 6. Load Timeslots
@app.route('/api/timeslots', methods=['GET'])
def get_timeslots():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
                    SELECT 
                        TimeSlotID,
                        TIME_FORMAT(StartTime, '%H:%i:%s') AS StartTime,
                        TIME_FORMAT(EndTime, '%H:%i:%s') AS EndTime,
                        IsBooked
                    FROM TimeSlot
                """
        cursor.execute(query)
        timeslots = cursor.fetchall()

        return jsonify({"success": True, "data": timeslots}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# 7. Delete Timeslot
@app.route('/api/timeslots/<int:timeslot_id>', methods=['DELETE'])
def delete_timeslot(timeslot_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "DELETE FROM TimeSlot WHERE TimeSlotID = %s"
        cursor.execute(query, (timeslot_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Timeslot not found"}), 404

        return jsonify({"success": True, "message": "Timeslot deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/api/myteam', methods=['POST'])
def get_my_team():
    try:
        data = request.get_json()
        user_email = data.get('email')

        if not user_email:
            return jsonify({"success": False, "message": "User not logged in"}), 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT Name, Email, Ranking, CreationDate FROM Team WHERE Email = %s"
        cursor.execute(query, (user_email,))
        team = cursor.fetchone()

        cursor.close()
        connection.close()

        if not team:
            return jsonify({"success": False, "message": "Team not found"}), 404

        return jsonify({"success": True, "data": team}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

#MyTeam page



