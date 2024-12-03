# SoccerMatch Scheduler

## Overview
SoccerMatch Scheduler is a web-based application that allows university students to book time slots on a soccer field, schedule matches, and manage team rankings. The platform includes features like user registration, login, match scheduling, and ranking visualization.

## Features
- **User Registration**: Teams can register with their team name, email, and password.
- **User Login**: Secure login system with password hashing (SHA256).
- **Match Scheduling**:
  - View and book available time slots.
  - Schedule matches with selected opponents or notify others to join.
- **Ranking System**: Rankings are updated based on match outcomes.
- **Notification System**: Notifications for match invites and updates.

## Technology Stack
### Frontend
- **HTML/CSS**: For structuring and styling the pages.
- **JavaScript**: For client-side interactions and API calls.

### Backend
- **Python Flask**: API development for user authentication and match scheduling.
- **MySQL**: Database for storing user, match, and notification data.


## Setup Instructions

### 1. Clone the Repository
- git clone https://github.com/your-username/soccermatch-scheduler.git
- Go to the project folder
  - cd CNG495-CloudComputing

### 2. Create Database
- Open MySQL Workbench and connect to your MySQL server.
- Open the SQL file (db.sql) in MySQL Workbench.
- Execute the script to create the database
- 
### 3. Database Configuration
- Open the backend/db_config.py file.
- Update the database configuration to match your local MySQL credentials

### 4. Start the Flask Server
- Navigate to the backend folder:
    - cd Backend
- Run Flask server
    - python app.py
### 5. Frontend Setup
- Navigate to Frontend folder
  - cd ../Frontend
- Serve HTML files
  - python -m http.server 8000
- Open http://127.0.0.1:8000/login.html 

## Contact
- Email
  - ilgin.savas@gmail.com
  - yigitberkatci@gmail.com
  - kutayoren78@gmail.com
- GitHub
  - ilginsavas
  - yigitberkataci
  - kutayoren1