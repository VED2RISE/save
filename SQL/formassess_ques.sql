DROP TABLE Formative_Assessment_Questions;


CREATE TABLE Formative_Assessment_Questions (
    Assessment_ID INT,
    Question_ID INT,
    FOREIGN KEY (Assessment_ID) REFERENCES Formative_Assessments(Assessment_ID),
    FOREIGN KEY (Question_ID) REFERENCES Multiple_Choice_Questions(Question_ID)
)