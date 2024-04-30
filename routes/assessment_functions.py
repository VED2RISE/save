from flask import Blueprint, Flask, render_template, request, jsonify, session, redirect, request
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
import json
import sqlite3


import sqlite3


assessment_bp = Blueprint('assessment_functions', __name__)


class MyAssessmentForm(FlaskForm):
    integer_choices = [(1, 1), (2, 2), (3,3), (4,4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10,10), (11,11), (12,12)]
    available_choices = [(1, "Yes"), (2, "No")]
    title = StringField("Assessment Title", validators=[DataRequired()])
    topic = StringField("Assessment Topic", validators=[DataRequired()])
    instructions = StringField("Assessment Instructions", validators=[DataRequired()])
    number_of_questions = SelectField("Select Number of Question", choices=integer_choices, coerce=str)
    available = SelectField("Would you like to release assessment now?", choices=available_choices, coerce=str)
    submit = SubmitField("Submit")

@assessment_bp.route('/assessments')
def assessments():
    try: 
        # Get Live Summative:
        conn = sqlite3.connect('upGradeDB.db') 
        cur = conn.cursor()

        # create the query 
        query = "SELECT * FROM Summative_Assessments WHERE Available = 1;"
        
        # execute query and retrieve results
        res = cur.execute(query)
        assessment_list = res.fetchall()

        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        summative_assessments = [dict(zip(columns, row)) for row in assessment_list]

        # Get Live Formative:
        # create the query 
        query = "SELECT * FROM Formative_Assessments WHERE Available = 1;"
        
        # execute query and retrieve results
        res = cur.execute(query)
        assessment_list = res.fetchall()

        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        formative_assessments = [dict(zip(columns, row)) for row in assessment_list]

        # Get inactive:
        # create the query 
        query = "SELECT * FROM Formative_Assessments WHERE Available = 2;"
        
        # execute query and retrieve results
        res = cur.execute(query)
        assessment_list = res.fetchall()

        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        inactive_assessments = [dict(zip(columns, row)) for row in assessment_list]


    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        
    finally:
        conn.close()

    return render_template('assessments.html', summative_assessments=summative_assessments, formative_assessments=formative_assessments, inactive_assessments=inactive_assessments)


@assessment_bp.route('/create_formative', methods=['GET', 'POST'])
def create_formative():

    form = MyAssessmentForm()
    if form.validate_on_submit():

        session['assessment_data'] = {
            'Title': form.title.data,
            'Topic': form.topic.data,
            'Instructions': form.instructions.data,
            'Number_of_questions': form.number_of_questions.data,
            'Available' : form.available.data } 

        print(session['assessment_data'])

        return redirect('/add_questions')

    return render_template('create_formative.html', form=form)


    
@assessment_bp.route('/add_question_to_session', methods=['POST'])
def add_question_to_session():
    if request.method == 'POST':
        data = request.json
        question_id = data.get('questionId')
        print(question_id)
        if question_id:
            # Retrieve the existing list of question IDs or initialize it if it doesn't exist
            question_ids = session.get('question_ids', [])
            # Append the new question ID to the list
            question_ids.append(question_id)
            # Update the session data
            session['question_ids'] = question_ids
            print(session['question_ids'] )
            return 'Question ID added to session', 200
        else:
            return 'Invalid request', 400

@assessment_bp.route('/remove_question_from_session', methods=['POST'])
def remove_question_from_session():
    if request.method == 'POST':
        data = request.json
        question_id = int(data.get('questionId'))
        print(question_id)
        if question_id:
            # Retrieve the existing list of question IDs or initialize it if it doesn't exist
            question_ids = session.get('question_ids', [])
            print(f"Question ids: {question_ids}")
            # Remove the question ID to the list
            question_ids.remove(str(question_id))
            # Update the session data
            session['question_ids'] = question_ids
            print(session['question_ids'] )
            return 'Question ID removed from session', 200
        else:
            return 'Invalid request', 400

@assessment_bp.route('/add_questions', methods=['GET', 'POST'])
def add_questions():
    assessment_data = session.get('assessment_data', {})

    if request.method == 'POST':
        data = request.json # Don't think I need this anymore
        print(data)

        question_ids = session.get('question_ids')
        print(question_ids)

        try:
            conn = sqlite3.connect('upGradeDB.db')
            cur = conn.cursor()

            # Insert the assessment into the assessments table
            cur.execute("INSERT INTO Formative_Assessments (Title, Topic, Instructions, No_Of_Questions, Available) VALUES (?,?,?,?,?)", (assessment_data.get('Title'), assessment_data.get('Topic'), assessment_data.get('Instructions'), assessment_data.get('Number_of_questions'), assessment_data.get('Available')))

            # Get the last inserted row ID (auto-incremented ID of the assessment)
            assessment_id = cur.lastrowid

            # Create entries in the assessment_questions table
            for question_id in question_ids:
                cur.execute("INSERT INTO Assessment_Questions (Assessment_id, Question_id) VALUES (?, ?)", (assessment_id, question_id))

            print("DB updated")
            # Commit the changes to the database
            conn.commit()

            # Close the database connection
            conn.close()
        
        except sqlite3.Error as e:
            # Handle the error (e.g., log, display an error message)
            print(f"SQLite Error: {e}")
            return 'Error occurred while saving assessment and questions'

        return redirect("/assessments")
    
    try:
        # Questions from Topic:
        conn = sqlite3.connect('upGradeDB.db') 
        cur = conn.cursor()

        Topic = assessment_data['Topic']
    

        # create the query 
        query = "SELECT * FROM Questions WHERE Topic=?;"
        
        # execute query and retrieve results
        res = cur.execute(query, (assessment_data.get('Topic'),))
        assessment_list = res.fetchall()

        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        questions = [dict(zip(columns, row)) for row in assessment_list]

        
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
    
    finally:
        conn.close()

    if session.get('question_ids'):
        question_ids = [int(question) for question in session.get('question_ids')]
        print(question_ids)
        return render_template('add_questions.html', questions=questions, question_ids=question_ids)
    
    return render_template('add_questions.html', questions=questions)


@assessment_bp.route('/submit_formative')
def submit_formative():
    assessment_data = session.get('assessment_data', {})

    question_ids = session.get('question_ids')

    try:
        conn = sqlite3.connect('upGradeDB.db')
        cur = conn.cursor()

        # Insert the assessment into the assessments table
        cur.execute("INSERT INTO Formative_Assessments (Title, Topic, Instructions, No_Of_Questions, Available) VALUES (?,?,?,?,?)", (assessment_data.get('Title'), assessment_data.get('Topic'), assessment_data.get('Instructions'), assessment_data.get('Number_of_questions'), assessment_data.get('Available')))

        # Get the last inserted row ID (auto-incremented ID of the assessment)
        assessment_id = cur.lastrowid

        # Create entries in the assessment_questions table
        for question_id in question_ids:
            cur.execute("INSERT INTO Assessment_Questions (Assessment_id, Question_id) VALUES (?, ?)", (assessment_id, question_id))

        print("DB updated")
        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()

        session['question_ids'] = []
    
    except sqlite3.Error as e:
        # Handle the error (e.g., log, display an error message)
        print(f"SQLite Error: {e}")
        return 'Error occurred while saving assessment and questions'

    return redirect("/assessments")


@assessment_bp.route('/edit_assessment/<int:assessmentID>', methods=['GET', 'POST'])
def edit_assessment(assessmentID):
    form = MyAssessmentForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            session['assessment_data'] = {
                'Title': form.title.data,
                'Topic': form.topic.data,
                'Instructions': form.instructions.data,
                'Number_of_questions': form.number_of_questions.data,
                'Available' : form.available.data,
                'Assessment_Id' : assessmentID }

            print(session['assessment_data'])

            return redirect('/edit_add_questions')

    try:
        conn = sqlite3.connect('upGradeDB.db') 
        cur = conn.cursor()

        res = cur.execute('SELECT * FROM Formative_Assessments WHERE Assessment_ID = ?', (assessmentID,))

        assessment_tup = cur.fetchone()
        print(assessment_tup)

        # Get column names dynamically
        columns = [column[0] for column in cur.description]
        # Convert the list of tuples to a list of dictionaries
        assessment_dict = dict(zip(columns, assessment_tup))
        print(assessment_dict)

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
    
    finally:
        conn.close()

    print("Now it should load page")
    return render_template('edit_assessment.html', assessment_dict=assessment_dict, form=form)

@assessment_bp.route('/edit_add_questions')
def edit_add_questions():
    assessment_data = session.get('assessment_data', {})
    print(f"Assessment data {assessment_data}")

    if request.method == 'POST':
        
        question_ids = session.get('question_ids')

        try:
            conn = sqlite3.connect('upGradeDB.db')
            cur = conn.cursor()

            # Insert the assessment into the assessments table
            cur.execute("INSERT INTO Formative_Assessments (Title, Topic, Instructions, No_Of_Questions, Available) VALUES (?,?,?,?,?)", (assessment_data.get('Title'), assessment_data.get('Topic'), assessment_data.get('Instructions'), assessment_data.get('Number_of_questions'), assessment_data.get('Available')))

            # Get the last inserted row ID (auto-incremented ID of the assessment)
            assessment_id = cur.lastrowid

            # Create entries in the assessment_questions table
            for question_id in question_ids:
                cur.execute("INSERT INTO Assessment_Questions (Assessment_id, Question_id) VALUES (?, ?)", (assessment_id, question_id))

            print("DB updated")
            # Commit the changes to the database
            conn.commit()

            # Close the database connection
            conn.close()
        
        except sqlite3.Error as e:
            # Handle the error (e.g., log, display an error message)
            print(f"SQLite Error: {e}")
            return 'Error occurred while saving assessment and questions'

        return redirect("/assessments")
    
    try:
        ## Question TOPIC stuff ##

        # Questions from Topic:
        conn = sqlite3.connect('upGradeDB.db') 
        cur = conn.cursor()

        Topic = assessment_data['Topic']
    

        # create the query 
        query = "SELECT * FROM Questions WHERE Topic=?;"
        
        # execute query and retrieve results
        res = cur.execute(query, (assessment_data.get('Topic'),))
        assessment_list = res.fetchall()

        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        topic_questions = [dict(zip(columns, row)) for row in assessment_list]
        

        ## ID STUFF for questions in assignment already ##
        
        ids = cur.execute("SELECT Question_Id from Assessment_Questions WHERE Assessment_Id =?;", (assessment_data.get('Assessment_Id'),))
        id_list = ids.fetchall()

        print(id_list)

        questions = []

        for ID in id_list:
            q = cur.execute("SELECT * FROM Questions WHERE Question_Id = ?", (ID[0],))
            q_res = q.fetchone()
            questions.append(q_res)
        
        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        current_questions = [dict(zip(columns, row)) for row in questions]

        
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
   
        
    finally:
        conn.close()

    session['question_ids'] = []
    
        

    return render_template ('edit_add_questions.html', topic_questions=topic_questions, current_questions=current_questions)

