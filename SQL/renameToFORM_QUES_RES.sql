DROP TABLE IF EXISTS Formative_Assessment_Questions;
DROP TABLE IF EXISTS Formative_Question_Results;
DROP TABLE IF EXISTS Formative_Assessment_Results;
DROP TABLE IF EXISTS Formative_Assessment_Tags;
DROP TABLE IF EXISTS Formative_Assessments;

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

CREATE TABLE Formative_Question_Results (
    Student_ID INT,
    Assessment_ID INT,
    Question_ID INT,
    Correct BOOLEAN,
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID),
    FOREIGN KEY (Assessment_ID) REFERENCES Assessments(Assessment_ID),
    FOREIGN KEY (Question_ID) REFERENCES Questions(Question_ID)
);

CREATE TABLE Formative_Assessment_Questions (
    Assessment_ID INT,
    Question_ID INT,
    FOREIGN KEY (Assessment_ID) REFERENCES Formative_Assessments(Assessment_ID),
    FOREIGN KEY (Question_ID) REFERENCES Multiple_Choice_Questions(Question_ID)
);

CREATE TABLE Formative_Assessment_Results (
    Student_ID INT,
    Assessment_ID INT,
    Time_Taken INT,
    Score INT,
    Max_Score INT,
    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID),
    FOREIGN KEY (Assessment_ID) REFERENCES Formative_Assessments(Assessment_ID)
);


CREATE TABLE Formative_Assessment_Tags (
	Assessment_ID,
	Tag_ID,
	FOREIGN KEY (Assessment_ID) REFERENCES Formative_Assessments(Assessment_ID),
	FOREIGN KEY (Tag_Id) REFERENCES Tags(Tag_Id)
	);