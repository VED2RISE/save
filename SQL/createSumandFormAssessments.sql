DROP TABLE Formative_Assessments;
DROP TABLE Summative_Assessments;

CREATE TABLE Formative_Assessments (
    Assessment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Title TEXT,
    Instructions TEXT,
	Difficulty TEXT,
    No_Of_Questions INT,
    Available BOOLEAN,
	Module_ID,
	Lecturer_ID,
	FOREIGN KEY (Module_ID) REFERENCES Modules(Module_ID),
    FOREIGN KEY (Lecturer_ID) REFERENCES Lecturers(Lecturer_ID)
	
);
CREATE TABLE Summative_Assessments (
    Assessment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Title TEXT,
    Instructions TEXT,
    Deadline DATE,
    Time_Limit INT,
    No_Of_Questions INT,
    Available BOOLEAN,
    Feedback_Date DATE,
	Module_ID,
	Lecturer_ID,
	FOREIGN KEY (Module_ID) REFERENCES Modules(Module_ID),
    FOREIGN KEY (Lecturer_ID) REFERENCES Lecturers(Lecturer_ID)
);