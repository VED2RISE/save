CREATE TABLE IF NOT EXISTS Tags (

	Tag_Id INTEGER PRIMARY KEY AUTOINCREMENT,

	Tag TEXT NOT NULL

 );

 

INSERT INTO Tags (Tag) VALUES (&quot;JavaScript&quot;);

INSERT INTO Tags (Tag) VALUES (&quot;Python&quot;);

INSERT INTO Tags (Tag) VALUES (&quot;Java&quot;);


CREATE TABLE Formative_Assessment_Tags (

	Assessment_ID,

	Tag_ID,

	FOREIGN KEY (Assessment_ID) REFERENCES Formative_Assessments(Assessment_ID),

	FOREIGN KEY (Tag_Id) REFERENCES Tags(Tag_Id)

	);

	INSERT INTO Formative_Assessment_Tags VALUES (1, 2);
	INSERT INTO Formative_Assessment_Tags VALUES (1, 1);
	INSERT INTO Formative_Assessment_Tags VALUES (2, 2);
	INSERT INTO Formative_Assessment_Tags VALUES (2, 3);


	
CREATE TABLE Summative_Assessment_Tags (

	Assessment_ID,

	Tag_ID,

	FOREIGN KEY (Assessment_ID) REFERENCES Summative_Assessments(Assessment_ID),

	FOREIGN KEY (Tag_Id) REFERENCES Tags(Tag_Id)

	);

INSERT INTO Summative_Assessment_Tags VALUES (1, 2);
INSERT INTO Summative_Assessment_Tags VALUES (1, 1);
INSERT INTO Summative_Assessment_Tags VALUES (2, 2);
INSERT INTO Summative_Assessment_Tags VALUES (2, 3);


DROP TABLE Question_Tags;

CREATE TABLE Question_Tags (

	Question_ID,

	Tag_ID,

	FOREIGN KEY (Question_ID) REFERENCES Questions(Question_ID),

	FOREIGN KEY (Tag_Id) REFERENCES Tags(Tag_Id)

	);

	

INSERT INTO Question_Tags VALUES (4, 1);

INSERT INTO Question_Tags VALUES (5, 1);

INSERT INTO Question_Tags VALUES (6, 1);

INSERT INTO Question_Tags VALUES (1, 2);

INSERT INTO Question_Tags VALUES (2, 2);

INSERT INTO Question_Tags VALUES (3, 2);

INSERT INTO Question_Tags VALUES (7, 3);

INSERT INTO Question_Tags VALUES (8, 3);

INSERT INTO Question_Tags VALUES (9, 3);t>


		