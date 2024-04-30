DROP TABLE Students;

CREATE TABLE Students (
    Student_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Student_Name VARCHAR(255),
);

INSERT INTO Students (Student_Name, 'Cohort_ID') VALUES ("Harry Jacobs",1);
INSERT INTO Students (Student_Name, 'Cohort_ID') VALUES ("Luke Cleverley",1);
INSERT INTO Students (Student_Name, 'Cohort_ID') VALUES ("Niall Brogan",1);
INSERT INTO Students (Student_Name, 'Cohort_ID') VALUES ("Thomas McMorran",1);
INSERT INTO Students (Student_Name, 'Cohort_ID') VALUES ("Chenchen Wang",1);
INSERT INTO Students (Student_Name, 'Cohort_ID') VALUES ("Anying Hu",1);

AlTER TABLE Students
ADD COLUMN Intake_Year INTEGER;

UPDATE Students
SET Intake_Year = 2023;