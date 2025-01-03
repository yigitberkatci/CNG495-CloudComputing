CREATE DATABASE IF NOT EXISTS SoccerMatch;
USE SoccerMatch;

CREATE TABLE Team (
    TeamID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Ranking INT CHECK (Ranking BETWEEN 1 AND 10),
    CreationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    isAskingForMatch BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE SoccerMatch (
    MatchID INT AUTO_INCREMENT PRIMARY KEY,
    Team1ID INT NOT NULL,
    Team2ID INT DEFAULT NULL,
    Score1 INT DEFAULT 0,
    Score2 INT DEFAULT 0,
    FOREIGN KEY (Team1ID) REFERENCES Team(TeamID) ON DELETE CASCADE,
    FOREIGN KEY (Team2ID) REFERENCES Team(TeamID) ON DELETE CASCADE
);


CREATE TABLE TimeSlot (
    TimeSlotID INT AUTO_INCREMENT PRIMARY KEY,
    Date DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    IsBooked BOOLEAN DEFAULT FALSE,
    MatchID INT DEFAULT NULL,
    FOREIGN KEY (MatchID) REFERENCES SoccerMatch(MatchID) ON DELETE SET NULL
);


CREATE TABLE Notification (
    NotificationID INT AUTO_INCREMENT PRIMARY KEY,
    SenderID INT NOT NULL,
    ReceiverID INT,
    TimeSlotID INT,
    Message TEXT NOT NULL,
    Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    NotificationType VARCHAR(50) NOT NULL,
    FOREIGN KEY (SenderID) REFERENCES Team(TeamID) ON DELETE CASCADE,
    FOREIGN KEY (ReceiverID) REFERENCES Team(TeamID) ON DELETE SET NULL,
    FOREIGN KEY (TimeSlotID) REFERENCES TimeSlot(TimeSlotID) ON DELETE SET NULL
);


DELIMITER $$

CREATE EVENT IF NOT EXISTS AddNewTimeslots
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE() + INTERVAL 1 DAY
DO
BEGIN
    DECLARE start_time TIME;
    DECLARE end_time TIME;
    DECLARE i INT DEFAULT 0;

    SET start_time = '17:00:00';
    SET end_time = '18:00:00';

    WHILE i < 5 DO
        INSERT INTO TimeSlot (Date, StartTime, EndTime, IsBooked, MatchID)
        VALUES (CURRENT_DATE() + INTERVAL 1 DAY, start_time, end_time, 0, NULL);

        SET start_time = ADDTIME(start_time, '01:00:00');
        SET end_time = ADDTIME(end_time, '01:00:00');
        SET i = i + 1;
    END WHILE;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER UpdateTeamRanking
AFTER UPDATE ON SoccerMatch
FOR EACH ROW
BEGIN
    -- Update Team Rankings
    UPDATE Team t
    LEFT JOIN (
        SELECT
            t.TeamID,
            COUNT(sm.MatchID) AS MatchesPlayed,
            SUM(CASE WHEN sm.Score1 > sm.Score2 AND sm.Team1ID = t.TeamID THEN 1
                     WHEN sm.Score2 > sm.Score1 AND sm.Team2ID = t.TeamID THEN 1
                     ELSE 0 END) AS MatchesWon
        FROM Team t
        LEFT JOIN SoccerMatch sm ON t.TeamID = sm.Team1ID OR t.TeamID = sm.Team2ID
        WHERE sm.Score1 IS NOT NULL AND sm.Score2 IS NOT NULL
        GROUP BY t.TeamID
    ) win_stats ON t.TeamID = win_stats.TeamID
    SET t.Ranking = COALESCE(
        GREATEST(1, LEAST(10, ROUND(
            (win_stats.MatchesWon * 100.0 / win_stats.MatchesPlayed)
            * win_stats.MatchesPlayed * 10, 2
        ))), 1) -- Ensure Ranking is within 1 to 10
    WHERE t.TeamID IN (NEW.Team1ID, NEW.Team2ID);
END $$

DELIMITER ;
