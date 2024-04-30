DROP TABLE IF EXISTS Modules;
DROP TABLE IF EXISTS Lecturers;

-- Create Lecturers table
CREATE TABLE Lecturers (
    Lecturer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Lecturer_Name VARCHAR(255)  
);

-- Create Modules table
CREATE TABLE Modules (
    Module_ID INTEGER PRIMARY KEY,
    Module_Title VARCHAR(255)
);

INSERT INTO Lecturers (Lecturer_Name) VALUES ("Ian Cooper");
INSERT INTO Lecturers (Lecturer_Name) VALUES ("David Humphreys");
INSERT INTO Lecturers (Lecturer_Name) VALUES ("Niko Potyka");
INSERT INTO Modules VALUES (119, "Computational Thinking");
INSERT INTO Modules VALUES (120, "Fundamentals of Programming");
INSERT INTO Modules VALUES (313, "Software Engineering");


