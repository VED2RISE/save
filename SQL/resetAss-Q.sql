DROP TABLE Assessment_Questions;

CREATE TABLE Assessment_Questions (
    Assessment_ID INT,
    Question_ID INT,
    PRIMARY KEY (Assessment_ID, Question_ID),
    FOREIGN KEY (Assessment_ID) REFERENCES Assessments(Assessment_ID),
    FOREIGN KEY (Question_ID) REFERENCES Questions(Question_ID)
)