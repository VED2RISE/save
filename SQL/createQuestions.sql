-- DROP TABLE Questions;

CREATE TABLE Questions (
    Question_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Question_Type INTEGER,
    Question TEXT,
    Answer TEXT,
    Feedback TEXT,
    Hint TEXT,
    Topic VARCHAR(255)
);
	
INSERT INTO Questions(Question_Type, Question, Answer, Feedback, Hint, Topic) 
VALUES 
(1, 'What is Python?', 'Python is an interpreted, high-level, general-purpose programming language.', 'Correct!', 'Python emphasizes code readability and its syntax allows programmers to express concepts in fewer lines of code.', 'Python'),
(1, 'What are the basic data types in Python?', 'The basic data types in Python are integer, float, string, boolean, list, tuple, dictionary, and set.', 'Excellent!', 'Remember these data types for Python.', 'Python'),
(1, 'How do you declare variables in Python?', 'You can declare variables in Python by assigning a value to them.', 'Great!', 'Remember that Python is dynamically typed.', 'Python'),
-- Add more Python questions as needed
-- JavaScript questions
(1, 'What is JavaScript?', 'JavaScript is a scripting language.', 'Good job!', 'Remember, its a scripting language.', 'JavaScript'),
(1, 'What are the basic data types in JavaScript?', 'The basic data types in JavaScript are string, number, boolean, null, undefined, and object.', 'Correct!', 'Check out the documentation for more details.', 'JavaScript'),
(1, 'How do you declare variables in JavaScript?', 'You can declare variables using the ''var'', ''let'', or ''const'' keywords.', 'Well done!', 'Remember to use the appropriate keyword.', 'JavaScript'),
-- Add more JavaScript questions as needed
-- Java questions
(1, 'What is Java?', 'Java is a high-level, class-based, object-oriented programming language.', 'Correct!', 'Java is designed to have as few implementation dependencies as possible.', 'Java'),
(1, 'What are the basic data types in Java?', 'The basic data types in Java are byte, short, int, long, float, double, char, and boolean.', 'Well done!', 'Remember these data types for Java.', 'Java'),
(1, 'How do you declare variables in Java?', 'You can declare variables in Java by specifying the data type followed by the variable name.', 'Nice job!', 'Java is statically typed, so you must declare the data type of the variable.', 'Java');
-- Add more Java questions as needed
