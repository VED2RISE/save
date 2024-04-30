
DROP TABLE IF EXISTS Options;
DROP TABLE IF EXISTS Question_Tags;
DROP TABLE IF EXISTS Multiple_Choice_Questions;


CREATE TABLE IF NOT EXISTS Multiple_Choice_Questions (
    Question_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Question TEXT NOT NULL,
    Correct_answer TEXT NOT NULL,
    Hint TEXT,
    Difficulty TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Options (
    Option_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Question_ID INTEGER,
    Option TEXT NOT NULL,
    FOREIGN KEY (Question_ID) REFERENCES Multiple_Choice_Questions(Question_ID)
);

CREATE TABLE IF NOT EXISTS Question_Tags (
    Tag_ID INTEGER NOT NULL,
    Question_ID INTEGER NOT NULL,
	FOREIGN KEY (Tag_ID) REFERENCES Tags(Tag_ID),
    FOREIGN KEY (Question_ID) REFERENCES Multiple_Choice_Questions(Question_ID)
);


INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty) 
VALUES ('What keyword is used to define a function in Python?', 'def', 'Easy');

INSERT INTO Options (Question_ID, Option)
VALUES (1, 'func'), (1, 'def'), (1, 'function'), (1, 'define');

INSERT INTO Question_Tags (Tag_ID, Question_ID)
VALUES (2, 1);

-- Inserting question 2
INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty)
VALUES ('Which of the following is not a primitive data type in Python?', 'array', 'Medium');

INSERT INTO Options (Question_ID, Option)
VALUES (2, 'int'), (2, 'float'), (2, 'string'), (2, 'array');

INSERT INTO Question_Tags (Tag_ID, Question_ID)
VALUES (2, 2);

-- Inserting question 3
INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty)
VALUES ('What does the `len()` function in Python return?', 'The number of elements in a list', 'Easy');

INSERT INTO Options (Question_ID, Option)
VALUES (3, 'The last element of a list'), (3, 'The number of elements in a list'), 
       (3, 'The sum of all elements in a list'), (3, 'The average of all elements in a list');

INSERT INTO Question_Tags (Tag_ID, Question_ID)
VALUES (2, 3);

-- Inserting question 4
INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty)
VALUES ('How do you declare a comment in Python?', '# Comment', 'Easy');

INSERT INTO Options (Question_ID, Option)
VALUES (4, '// Comment'), (4, '/* Comment */'), (4, '# Comment'), (4, '-- Comment');

INSERT INTO Question_Tags (Tag_ID, Question_ID)
VALUES (2, 4);

-- Inserting question 5
INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty)
VALUES ('What is the output of `2 ** 3` in Python?', '8', 'Easy');

INSERT INTO Options (Question_ID, Option)
VALUES (5, '5'), (5, '8'), (5, '6'), (5, '9');

INSERT INTO Question_Tags (Tag_ID, Question_ID)
VALUES (2, 5);


-- Inserting questions for JavaScript
INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty)
VALUES 
    ('What is the file extension for JavaScript files?', '.js', 'Easy'),
    ('Which keyword is used to declare a variable in JavaScript?', 'var', 'Easy'),
    ('What does "NaN" stand for in JavaScript?', 'Not a Number', 'Medium'),
    ('Which of the following is not a JavaScript framework?', 'Spring', 'Hard'),
    ('What does the "===" operator do in JavaScript?', 'Strict equality comparison', 'Medium');

-- Inserting questions for Java
INSERT INTO Multiple_Choice_Questions (Question, Correct_Answer, Difficulty)
VALUES 
    ('Which data type is used to store a single character in Java?', 'char', 'Easy'),
    ('What is the output of "System.out.println(5 + 3 + \"Java\")" in Java?', '8Java', 'Easy'),
    ('Which keyword is used to define a constant in Java?', 'final', 'Medium'),
    ('What does the "public" access modifier do in Java?', 'Allows access from any other class', 'Hard'),
    ('Which of the following is not a Java IDE?', 'Visual Studio Code', 'Medium');

-- Inserting question_tags
INSERT INTO Question_Tags (Tag_ID, Question_ID)
VALUES 
    (1, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the file extension for JavaScript files?')),
    (1, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to declare a variable in JavaScript?')),
    (1, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does "NaN" stand for in JavaScript?')),
    (1, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a JavaScript framework?')),
    (1, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "===" operator do in JavaScript?')),
    (3, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which data type is used to store a single character in Java?')),
    (3, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the output of "System.out.println(5 + 3 + \"Java\")" in Java?')),
    (3, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to define a constant in Java?')),
    (3, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "public" access modifier do in Java?')),
    (3, (SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a Java IDE?'));

-- Inserting options
INSERT INTO Options (Question_ID, Option)
VALUES 
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the file extension for JavaScript files?'), '.js'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the file extension for JavaScript files?'), '.css'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the file extension for JavaScript files?'), '.html'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the file extension for JavaScript files?'), '.php'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to declare a variable in JavaScript?'), 'var'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to declare a variable in JavaScript?'), 'let'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to declare a variable in JavaScript?'), 'const'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to declare a variable in JavaScript?'), 'function'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does "NaN" stand for in JavaScript?'), 'Not a Number'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does "NaN" stand for in JavaScript?'), 'Not a Null'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does "NaN" stand for in JavaScript?'), 'Not a Name'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does "NaN" stand for in JavaScript?'), 'Not a Nothing'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a JavaScript framework?'), 'Spring'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a JavaScript framework?'), 'Angular'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a JavaScript framework?'), 'Vue'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a JavaScript framework?'), 'React'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "===" operator do in JavaScript?'), 'Strict equality comparison'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "===" operator do in JavaScript?'), 'Type and value comparison'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "===" operator do in JavaScript?'), 'Value comparison only'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "===" operator do in JavaScript?'), 'Type comparison only'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which data type is used to store a single character in Java?'), 'char'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which data type is used to store a single character in Java?'), 'int'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which data type is used to store a single character in Java?'), 'String'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which data type is used to store a single character in Java?'), 'float'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the output of "System.out.println(5 + 3 + \"Java\")" in Java?'), '8Java'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the output of "System.out.println(5 + 3 + \"Java\")" in Java?'), 'Java'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the output of "System.out.println(5 + 3 + \"Java\")" in Java?'), '5Java'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What is the output of "System.out.println(5 + 3 + \"Java\")" in Java?'), '35'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to define a constant in Java?'), 'const'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to define a constant in Java?'), 'final'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to define a constant in Java?'), 'static'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which keyword is used to define a constant in Java?'), 'var'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "public" access modifier do in Java?'), 'Allows access from any other class'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "public" access modifier do in Java?'), 'Allows access only within the same package'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "public" access modifier do in Java?'), 'Allows access only within the same class'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'What does the "public" access modifier do in Java?'), 'Allows access only within subclasses'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a Java IDE?'), 'Eclipse'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a Java IDE?'), 'IntelliJ IDEA'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a Java IDE?'), 'Visual Studio'),
    ((SELECT Question_ID FROM Multiple_Choice_Questions WHERE Question = 'Which of the following is not a Java IDE?'), 'NetBeans');

