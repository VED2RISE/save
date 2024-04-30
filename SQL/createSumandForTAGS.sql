DROP TABLE Formative_Assessments;
DROP TABLE Summative_Assessments;

CREATE TABLE Formative_Assessments (
    Assessment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Title TEXT,
    Instructions TEXT,
    No_Of_Questions INT,
    Available BOOLEAN
);
CREATE TABLE Summative_Assessments (
    Assessment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Title TEXT,
    Instructions TEXT,
    Deadline DATE,
    Time_Limit INT,
    No_Of_Questions INT,
    Available BOOLEAN,
    Feedback_Date DATE
);

INSERT INTO Formative_Assessments (Title, Instructions, No_Of_Questions, Available)
VALUES ("Beginner JS",  "Complete the following questions to the best of your ability",
10, True);

INSERT INTO Formative_Assessments (Title, Instructions, No_Of_Questions, Available)
VALUES ("Beginner Python",  "Answer each question, even if you're not sure", 10, True);

INSERT INTO Summative_Assessments (Title, Instructions, Deadline, Time_Limit, No_Of_Questions, Available, Feedback_Date)
VALUES ("JS Test",  "This is the summative assesment for the module", "2024-04-02", 60, 10, True, "2024-04-15");

INSERT INTO Summative_Assessments (Title,  Instructions, Deadline, Time_Limit, No_Of_Questions, Available, Feedback_Date)
VALUES ("Python Test",  "Python questions from the moduke", "2024-04-04", 60, 10, True, "2024-04-20");