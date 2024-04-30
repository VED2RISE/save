from flask import Flask, flash, render_template, request, session, redirect, jsonify, url_for
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from functions import getListofDict, getDict
from wtforms import SelectField, SelectMultipleField, StringField, TextAreaField, IntegerField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, Length
from jinja2 import Environment
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = "super secret key"


DATABASE = 'upGradeDB.db'
app = Flask(__name__)
app.secret_key = 'team09'

# needed for do statement on add assignment questions
environment = Environment(extensions=['jinja2.ext.do'])
app.jinja_env.add_extension('jinja2.ext.do')



def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DROP TABLE IF EXISTS posts')  # Drop the table if it exists
        conn.execute('''CREATE TABLE posts
                        (id INTEGER PRIMARY KEY,
                         username TEXT,
                         assessment_id INTEGER, 
                         comment_text TEXT,
                         time_posted DATETIME, 
                        reply TEXT)''')
        conn.commit()

init_db()


@app.route('/replies')
def user_replies():
    username = current_user.username  # Assumes the username is stored in session
    if not username:
        return "You must be logged in to view this page", 403

    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row  # Makes row results accessible as dictionaries
        cur = conn.cursor()
        cur.execute('SELECT * FROM posts WHERE username = ? ORDER BY time_posted DESC', (username,))
        comments_and_replies = cur.fetchall()
        print(comments_and_replies)
    return render_template('student_replies.html', comments_replies=comments_and_replies)


@app.route('/responses', methods=['GET', 'POST'])
def handle_responses():
    if request.method == 'POST':
        comment_id = request.form.get('comment_id')
        reply = request.form.get('reply')
        reply = current_user.username + " " + "replied: " + reply
        action = request.form.get('action')

        with sqlite3.connect(DATABASE) as conn:
            if action == "add":
                conn.execute('UPDATE posts SET reply = ? WHERE id = ? AND reply IS NULL', (reply, comment_id))
                conn.commit()
                print()
                return jsonify(success=True, reply=reply)
            elif action == "delete":
                conn.execute('UPDATE posts SET reply = NULL WHERE id = ?', (comment_id,))
                conn.commit()
                return jsonify(success=True)

        return jsonify(success=False, message="Action failed")

    # Fetch all comments and replies for all assessments
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY assessment_id')
        comments = cursor.fetchall()
    print(comments)

    return render_template('questions.html', comments=comments)

@app.route('/post_comment/<int:assessmentID>', methods=['POST'])
def post_comment(assessmentID):
    username = current_user.username  # Ensure current_user is correctly imported and used
    comment = request.form['commentText']
    print(comment)
    time_posted = datetime.now()

    if not comment:  # Check if the comment is empty
        flash("Comment is empty, please write something.")
        return redirect(url_for('formative_take_assessment', assessmentID=assessmentID))

    try:
        with sqlite3.connect(DATABASE) as conn:
            # Check if this user has already posted a comment for this assessment
            existing_comment = conn.execute('SELECT * FROM posts WHERE username = ? AND assessment_id = ?', 
                                            (username, assessmentID)).fetchone()
            if existing_comment:
                flash("You have already posted a comment for this assessment.")
                return redirect(url_for('formative_take_assessment', assessmentID=assessmentID))

            # Insert new comment with username
            conn.execute('INSERT INTO posts (username, assessment_id, comment_text, time_posted) VALUES (?, ?, ?, ?)',
                         (username, assessmentID, comment, time_posted))
            conn.commit()
            flash("Comment posted successfully.")
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        flash('Error occurred while posting comment')
        return redirect(url_for('formative_take_assessment', assessmentID=assessmentID))

    return redirect(url_for('formative_take_assessment', assessmentID=assessmentID))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('DELETE FROM posts WHERE id = ?', (comment_id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting comment: {e}")
        return 'Error occurred while deleting comment'
    return redirect(request.referrer)

@app.route('/formative_take_assessment/<int:assessmentID>')
def formative_take_assessment(assessmentID):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row  # Allows dictionary-like access to columns
            cur = conn.cursor()

            # Fetch the details of the assessment
            assessment_query = "SELECT * FROM Formative_Assessments WHERE Assessment_ID = ?"
            assessment_res = cur.execute(assessment_query, (assessmentID,))
            assessment = dict(assessment_res.fetchone())  # Convert the result to a dictionary

            # Get the MCQs and related information
            mcq_query = """SELECT MCQ.*
                           FROM Multiple_Choice_Questions MCQ
                           JOIN Formative_Assessment_Questions FAQ ON MCQ.Question_ID = FAQ.Question_ID
                           JOIN Formative_Assessments FA ON FAQ.Assessment_ID = FA.Assessment_ID
                           WHERE FA.Assessment_ID = ?;"""
            mcq_res = cur.execute(mcq_query, (assessmentID,))
            questions = [dict(row) for row in mcq_res.fetchall()]

            # Get options for MCQs
            question_options = {}
            for question in questions:
                options_res = cur.execute('SELECT Option FROM Options WHERE Question_ID = ?', (question['Question_ID'],))
                question_options[question['Question_ID']] = [option['Option'] for option in options_res.fetchall()]

            # Fetch only the current user's comment for the assessment
            comment_query = 'SELECT * FROM posts WHERE assessment_id = ? AND username = ?'
            comments_res = cur.execute(comment_query, (assessmentID, current_user.username))
            comments = [dict(comment) for comment in comments_res.fetchall()]
            print(1)
            print(comments)

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        return 'Error occurred while preparing assessment'

    return render_template("formative_take_assessment.html", assessment=assessment, questions=questions, question_options=question_options, comments=comments)


# *********Pre-set for Login*********
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self,username,role, id):
        self.username = username
        self.role = role
        self.user_id = id
    def get_id(self):
        return f"{self.role}_{self.username}"

@login_manager.user_loader
def load_user(user_id):
    role, username = user_id.split('_', 1)
    user = None
    conn =sqlite3.connect(DATABASE)
    cur = conn.cursor()
    if role == "lecturer":
        cur.execute("SELECT * FROM Lecturers WHERE Lecturer_Name = ?", (username,))
        user = cur.fetchone()
    elif role == "student":
        cur.execute("SELECT * FROM Students WHERE Student_Name = ?", (username,))
        user = cur.fetchone()
    conn.close()
    user_id = user[0]
    if user:
        return User(username, role, user_id)
    
    return None
    

# ********************************/HOME*********************************
@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    # check if user has logged in
    if current_user.is_authenticated:
        return render_template('1_home.html', logged_in = True, role = current_user.role, username = current_user.username , id = current_user.user_id)
    else:
        return render_template('1_home.html', logged_in = False)

# ********************************/LOGIN*********************************
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', default="Error")
        role = request.form.get('role')

        user = None
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        if role == "lecturer":
            cur.execute("SELECT * FROM Lecturers WHERE Lecturer_Name = ?", (username,))
            user = cur.fetchone()
            cur.execute("SELECT Lecturer_ID FROM Lecturers WHERE Lecturer_Name = ?", (username,))
            lecturerid = cur.fetchone()
            session['lecturer_id'] = lecturerid

        elif role == "student":
            cur.execute("SELECT * FROM Students WHERE Student_Name = ?", (username,))
            user = cur.fetchone()     
            cur.execute("SELECT Student_ID FROM Students WHERE Student_Name = ?", (username,))
            studentid = cur.fetchone()
            session['student_id'] = studentid
        conn.close()
        user_id = user[0]


        if user:
            user_obj = User(username, role, user_id)
            login_user(user_obj)
            return render_template('1_home.html')
        else:
            flash('Invalid username or role')
    return render_template('2_login.html')


       

# ********************************LOGOUT*********************************
@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return render_template('1_home.html')


available_choices = [("",""), (1, "Yes"), (2, "No")]
difficulty_choices = [(""), ("Beginner"), ("Intermediate"), ("Advanced")]
module_choices = [ (119, "Computational Thinking"), (120, "Fundamentals of Programming"),(313, "Software Engineering")]
# Create a Form Class
### Create / Edit Assessment Form
class MyAssessmentForm(FlaskForm):
    
    title = StringField("Assessment Title", validators=[DataRequired()])
    module = SelectField("Select module", validators=[DataRequired()], choices=module_choices, coerce=str, render_kw={"placeholder": "Select module"})
    difficulty = SelectField("Select difficulty", validators=[DataRequired()],choices=difficulty_choices, coerce=str, render_kw={"placeholder": "Select difficulty"})
    instructions = StringField("Assessment Instructions", validators=[DataRequired()])
    available = SelectField("Would you like to release assessment now?", validators=[DataRequired()],choices=available_choices, coerce=str, render_kw={"placeholder": "Select availability"})
    submit = SubmitField("Submit")

### Search Assessment Form
class SearchAssessmentForm(FlaskForm):
    title = StringField("Title")
    available = SelectField("Available", choices=available_choices, coerce=str)
    difficulty = SelectField("Difficulty", choices=difficulty_choices, coerce=str)
    submit = SubmitField("Submit")

@app.route('/formative_assessments_lecturer', methods=['GET', 'POST'])
@app.route('/formative_assessments_student', methods=['GET', 'POST'])

def formative_assessments():

    # Connect to db:
    conn = sqlite3.connect(DATABASE) 
    cur = conn.cursor()
    # Get all tags
    res = cur.execute("SELECT * FROM Tags")
    tag_list = getListofDict(res, cur)

    # Get FA base
    fa_query = """ SELECT FA.*, GROUP_CONCAT(t.Tag, " ") AS Tags, GROUP_CONCAT(t.Tag_Id, " ") AS Tag_Ids
                FROM Formative_Assessments AS FA 
                LEFT JOIN Formative_Assessment_Tags AS ST ON ST.Assessment_ID = FA.Assessment_ID
                LEFT JOIN Tags AS t ON ST.Tag_ID = t.Tag_Id
                WHERE Available = ? OR ?
                GROUP BY FA.Assessment_ID, FA.Title;"""


    if request.method == 'POST':

        # Get form/session data
        available = 1
        tag_ids = session['Tag_Ids']
        difficulty = request.form.get("difficulty")

        # If lecturer logged in they can see inactive assessments too
        if current_user.role == 'lecturer':
            available = request.form.get("available")
            print(available)
            if available != None:
                available = int(available)

        
        try:
            # Get ALL questions
                      
            res = cur.execute(fa_query, (1,2))

            formative_assessments = getListofDict(res, cur)


            for ass in formative_assessments:
                if ass['Tags'] != None:
                    ass["Tags"] = ass["Tags"].split(" ")
                    ass['Tag_Ids'] = ass['Tag_Ids'].split(" ")


            search_results = []

            if difficulty == None:
                difficulty = ""

            # Search dictionary for matching assessments
            for ass in formative_assessments:
                if available == ass['Available'] or available == None:
                    search_results.append(ass)
            
            for ass in search_results:
                if difficulty != ass['Difficulty']:
                    search_results.remove(ass)

            matching_tags = 0
            for ass in search_results:
                for tag_id in tag_ids:
                    if tag_id in ass['Tag_Ids']:
                        matching_tags+=1
                if matching_tags == 0:
                    search_results.remove(ass)
     
            conn.commit()

            session['Tag_Ids'] = []
            print(f"Search results{search_results}")

            if current_user.role == 'lecturer':
                print("lecturer")
                return render_template('formative_assessments_lecturer.html', search_results=search_results, tag_list=tag_list)
            if current_user.role == 'student':
                return render_template('formative_assessments_student.html', search_results=search_results, tag_list=tag_list )
        
        except sqlite3.Error as e:
            print(f"SQLite Error: {e}")
            
    try: 
        
        
        # execute fa_query and retrieve results
        res = cur.execute(fa_query, (1,0))

        formative_assessments = getListofDict(res, cur)

        for ass in formative_assessments:
            if ass['Tags'] != None:
                ass["Tags"] = ass["Tags"].split(" ")
                ass['Tag_Ids'] = ass['Tag_Ids'].split(" ")

    

        # Get inactive        
        # execute fa_query and retrieve results
        res = cur.execute(fa_query, (2,0))
        
        inactive_assessments = getListofDict(res, cur)
        print(inactive_assessments)
        for ass in inactive_assessments:
            if ass['Tags'] != None:
                ass["Tags"] = ass["Tags"].split(" ")
                ass['Tag_Ids'] = ass['Tag_Ids'].split(" ")

        conn.commit()

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        
    
    
    if current_user.role == 'student':
        return render_template('formative_assessments_student.html', formative_assessments=formative_assessments, tag_list=tag_list)

    if current_user.role == 'lecturer':
        return render_template('formative_assessments_lecturer.html', formative_assessments=formative_assessments, inactive_assessments=inactive_assessments, tag_list=tag_list)


@app.route('/formative_create_assessment', methods=['GET', 'POST'])
def create_formative():

    form = MyAssessmentForm()
    if form.validate_on_submit():

        session['assessment_data'] = {
            'Title': form.title.data,
            'Tags': session['Tag_Ids'],
            'Module_Id': form.module.data,
            'Lecturer_Id': current_user.user_id,
            'Difficulty': form.difficulty.data,
            'Instructions': form.instructions.data,
            'Available' : form.available.data } 

        print(session['assessment_data'])

        return redirect('/formative_add_questions')

    try:
        # Get Live Summative:
        conn = sqlite3.connect(DATABASE) 
        cur = conn.cursor()

        res = cur.execute("SELECT * FROM Tags")
        tag_list = getListofDict(res, cur)
        

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        
    finally:
        conn.close()



    return render_template('formative_create_assessment.html', form=form, tag_list=tag_list)

@app.route('/add_tag_to_session', methods=['POST'])
def add_tag_to_session():
    if request.method == 'POST':
        data = request.json
        tag_id = data.get('tagId')
        print(tag_id)
        if tag_id:
            # Retrieve the existing list of tag IDs or initialize it if it doesn't exist
            tag_ids = session.get('Tag_Ids', [])
            # Append the new tag ID to the list
            tag_ids.append(tag_id)
            # Update the session data
            session['Tag_Ids'] = tag_ids
            return 'tag ID added to session', 200
        else:
            return 'Invalid request', 400

@app.route('/remove_tag_from_session', methods=['POST'])
def remove_tag_from_session():
    if request.method == 'POST':
        data = request.json
        tag_id = int(data.get('tagId'))
        print(tag_id)
        if tag_id:
            # Retrieve the existing list of tag IDs or initialize it if it doesn't exist
            tag_ids = session.get('Tag_Ids', [])
            print(f"tag ids: {tag_ids}")
            # Remove the tag ID to the list
            tag_ids.remove(str(tag_id))
            # Update the session data
            session['Tag_Ids'] = tag_ids
            print(session['Tag_Ids'] )
            return 'tag ID removed from session', 200
        else:
            return 'Invalid request', 400
        
@app.route('/add_question_to_session', methods=['POST'])
def add_question_to_session():
    if request.method == 'POST':
        data = request.json
        question_id = data.get('questionId')
        print(question_id)
        if question_id:
            # Retrieve the existing list of question IDs or initialize it if it doesn't exist
            question_ids = session.get('question_ids', [])
            # Append the new question ID to the list
            question_ids.append(int(question_id))
            # Update the session data
            session['question_ids'] = question_ids
            print(session['question_ids'] )
            return 'Question ID added to session', 200
        else:
            return 'Invalid request', 400

@app.route('/remove_question_from_session', methods=['POST'])
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
            question_ids.remove(int(question_id))
            # Update the session data
            session['question_ids'] = question_ids
            print(session['question_ids'] )
            return 'Question ID removed from session', 200
        else:
            return 'Invalid request', 400

@app.route('/formative_add_questions', methods=['GET', 'POST'])
def formative_add_questions():


    try:
        # Questions from Topic:
        conn = sqlite3.connect(DATABASE) 
        cur = conn.cursor()

        session['question_ids'] = []
        ids = session['Tag_Ids']
        print(ids)
   
        # create the query 
        query = """SELECT MCQ.*, t.*
            FROM Multiple_Choice_Questions MCQ
            JOIN Question_Tags qt ON MCQ.Question_ID = qt.Question_ID
            JOIN Tags t ON qt.Tag_Id = t.Tag_Id
            WHERE t.Tag_Id IN ({})""".format(', '.join(['?'] * len(ids)))

        

        # execute query and retrieve results
        res = cur.execute(query, ids)
        tag_questions = getListofDict(res, cur)

        print(tag_questions)
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
    
    finally:
        conn.close()

    if session.get('question_ids'):
        question_ids = [int(question) for question in session.get('question_ids')]
        print(question_ids)
        return render_template('formative_add_questions.html', tag_questions=tag_questions, question_ids=question_ids)
    
    return render_template('formative_add_questions.html', tag_questions=tag_questions)


@app.route('/formative_submit_new_assessment')
def submit_formative():
    assessment_data = session.get('assessment_data', {})

    question_ids = session.get('question_ids')
    tag_ids = session.get('Tag_Ids')
    no_of_qs = len(session.get('question_ids'))

    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        # Insert the assessment into the assessments table
        cur.execute("INSERT INTO Formative_Assessments (Title, Module_ID, Difficulty, Instructions, No_Of_Questions, Available, Lecturer_ID) VALUES (?,?,?,?,?,?,?)", (assessment_data.get('Title'), assessment_data.get('Module_Id') ,assessment_data.get('Difficulty'), assessment_data.get('Instructions'), no_of_qs, assessment_data.get('Available'), assessment_data.get('Lecturer_Id')))

        # Get the last inserted row ID (auto-incremented ID of the assessment)
        assessment_id = cur.lastrowid

        # Create entries in the assessment_questions table
        for question_id in question_ids:
            cur.execute("INSERT INTO Formative_Assessment_Questions (Assessment_ID, Question_ID) VALUES (?, ?)", (assessment_id, question_id))

        for tag_id in tag_ids:
            cur.execute("INSERT INTO Formative_Assessment_Tags VALUES (?,?)", (assessment_id, tag_id))
        print("DB updated")
        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()

        session['question_ids'] = []
        session['Tag_Ids'] = []
    
    except sqlite3.Error as e:
        # Handle the error (e.g., log, display an error message)
        print(f"SQLite Error: {e}")
        return 'Error occurred while saving assessment and questions'

    return redirect("/formative_assessments_lecturer")


@app.route('/formative_edit_assessment/<int:assessmentID>', methods=['GET', 'POST'])
def edit_assessment(assessmentID):
    form = MyAssessmentForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            session['assessment_data'] = {
                'Title': form.title.data,
                'Tags': session['Tag_Ids'],
                'Module_Id': form.module.data,
                'Lecturer_Id': current_user.user_id,
                'Difficulty': form.difficulty.data,
                'Instructions': form.instructions.data,
                'Available' : form.available.data } 

            print(f"Assessment data on submit: {session['assessment_data']}")

            return redirect(f'/formative_edit_add_questions/{assessmentID}')

    try:
        conn = sqlite3.connect(DATABASE) 
        cur = conn.cursor()

        res = cur.execute('SELECT * FROM Formative_Assessments WHERE Assessment_ID = ?', (assessmentID,))

        assessment_tup = res.fetchone()
        print(assessment_tup)

        # Get column names dynamically
        columns = [column[0] for column in cur.description]
        # Convert the list of tuples to a list of dictionaries
        assessment_dict = dict(zip(columns, assessment_tup))

        res = cur.execute("SELECT T.* FROM Tags T JOIN Formative_Assessment_Tags FAT ON T.Tag_Id = FAT.Tag_ID WHERE FAT.Tag_ID = ?", (assessmentID,))
        ass_tags = getListofDict(res, cur)
        
        res = cur.execute("SELECT * FROM Tags")
        tag_list = getListofDict(res, cur)

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
    
    finally:
        conn.close()

    print("Now it should load page")
    return render_template('formative_edit_assessment.html', assessment_dict=assessment_dict, form=form, ass_tags=ass_tags, tag_list=tag_list)

@app.route('/formative_edit_add_questions/<int:assessmentID>')
def edit_add_questions(assessmentID):

    assessment_data = session.get('assessment_data', {})
    assessment_id = assessmentID 
    print(f"Assessment data {assessment_data}")
    
    try:
        ## Question TOPIC stuff ##

        # Questions from Topic:
        conn = sqlite3.connect(DATABASE) 
        cur = conn.cursor()

        session['question_ids'] = []
        ids = session['Tag_Ids']
        print(ids)
   
        # create the query 
        query = """SELECT q.*, t.*
            FROM Multiple_Choice_Questions AS q
            JOIN Question_Tags qt ON q.Question_ID = qt.Question_ID
            JOIN Tags t ON qt.Tag_Id = t.Tag_Id
            WHERE t.Tag_Id IN ({})""".format(', '.join(['?'] * len(ids)))

        

        # execute query and retrieve results
        res = cur.execute(query, ids)
        tag_questions = getListofDict(res, cur)
        

        ## ID STUFF for questions in assignment already ##
        print(f"ass_id:{assessment_id}")
        ids = cur.execute("SELECT Question_ID from Formative_Assessment_Questions WHERE Assessment_ID =?;", (assessment_id,))
        id_list = ids.fetchall()
        
        print(f"ID List: {id_list}" )

        questions = []
        session['question_ids'] = []

        for ID in id_list:
            q = cur.execute("SELECT * FROM Multiple_Choice_Questions WHERE Question_Id = ?", (ID[0],))
            q_res = q.fetchone()
            questions.append(q_res)

            session['question_ids'].append(ID[0])
        
        # Get column names dynamically
        columns = [column[0] for column in cur.description]

        # Convert the list of tuples to a list of dictionaries
        current_questions = [dict(zip(columns, row)) for row in questions]

        
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
   
        
    finally:
        conn.close()

    return render_template ('formative_edit_add_questions.html', tag_questions=tag_questions, current_questions=current_questions, assessment_id=assessment_id)



@app.route('/formative_update_assessment/<int:assessmentID>')
def update_formative(assessmentID):
    assessment_data = session.get('assessment_data', {})
    assessment_id = assessmentID

    question_ids = session.get('question_ids')
    no_of_qs = len(session.get('question_ids'))
    print(f"question ids: {question_ids}")

    tag_ids = session.get('Tag_Ids')

    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        # Insert the assessment into the assessments table
        cur.execute("UPDATE Formative_Assessments SET Title = ? WHERE Assessment_ID = ? AND Title != ?", (assessment_data.get('Title'), assessment_id, assessment_data.get('Title')))
        cur.execute("UPDATE Formative_Assessments SET Module_ID = ? WHERE Assessment_ID = ? AND Module_ID != ?", (assessment_data.get('Module_Id'), assessment_id, assessment_data.get('Module_Id')))
        cur.execute("UPDATE Formative_Assessments SET Difficulty = ? WHERE Assessment_ID = ? AND Difficulty != ?", (assessment_data.get('Difficulty'), assessment_id, assessment_data.get('Difficulty')))
        cur.execute("UPDATE Formative_Assessments SET Instructions = ? WHERE Assessment_ID = ? AND Instructions != ?", (assessment_data.get('Instructions'), assessment_id, assessment_data.get('Instructions')))
        cur.execute("UPDATE Formative_Assessments SET No_Of_Questions = ? WHERE Assessment_ID = ? AND No_Of_Questions != ?", (no_of_qs, assessment_id, no_of_qs))
        cur.execute("UPDATE Formative_Assessments SET Available = ? WHERE Assessment_ID = ? AND Available != ?", (assessment_data.get('Available'), assessment_id, assessment_data.get('Available')))



        # Create entries in the assessment_questions table
        cur.execute("DELETE FROM Formative_Assessment_Questions WHERE Assessment_ID = ?", (assessment_id,))
        for question_id in question_ids:
            cur.execute("INSERT INTO Formative_Assessment_Questions (Assessment_ID, Question_ID) VALUES (?,?)", (assessment_id, int(question_id)))
        
        cur.execute("DELETE FROM Formative_Assessment_Tags WHERE Assessment_ID = ?", (assessment_id,))
        for tag_id in tag_ids:
            cur.execute("INSERT INTO Formative_Assessment_Tags (Assessment_ID, Tag_ID) VALUES (?,?)", (assessment_id, int(tag_id)))
            

        conn.commit()

        # Close the database connection
        conn.close()
        
        session['question_ids'] = []
        session['Tag_Ids'] = []
    
    except sqlite3.Error as e:
        # Handle the error (e.g., log, display an error message)
        print(f"SQLite Error: {e}")
        return 'Error occurred while saving assessment and questions'

    return redirect("/formative_assessments_lecturer")

@app.route('/formative_delete_assessment/<int:assessmentID>')
def delete_formative_assessment(assessmentID):
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute("DELETE FROM Formative_Assessments WHERE Assessment_ID = ? ", (assessmentID,))
        cur.execute("DELETE FROM Formative_Assessment_Questions WHERE Assessment_ID =?", (assessmentID,))
        cur.execute("DELETE FROM Formative_Assessment_Tags WHERE Assessment_ID =?", (assessmentID,))                    
        
        conn.commit()

        # Close the database connection
        conn.close()
            
    except sqlite3.Error as e:
        # Handle the error (e.g., log, display an error message)
        print(f"SQLite Error: {e}")
        return 'Error occurred while saving assessment and questions'

    return redirect("/formative_assessments_lecturer")



####################### STUDENTS #######################

@app.route('/formative_assessments_student')
def formative_assessments_student():
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        # Get Live Formative:
        
        query = """SELECT FA.*, GROUP_CONCAT(t.Tag, " ") AS tags, t.Tag_Id 
        FROM Formative_Assessments AS FA 
        LEFT JOIN Formative_Assessment_Tags AS ST ON ST.Assessment_ID = FA.Assessment_ID
        LEFT JOIN Tags AS t ON ST.Tag_ID = t.Tag_Id 
        WHERE Available = 1
        GROUP BY FA.Assessment_ID, FA.Title;"""
        res = cur.execute(query )

        assessments = getListofDict(res,cur)

        
        conn.commit()

        # Close the database connection
        conn.close()
            
    except sqlite3.Error as e:
        # Handle the error (e.g., log, display an error message)
        print(f"SQLite Error: {e}")
        return 'Error occurred while saving assessment and questions'

    return render_template("formative_assessments_student.html", formative_assessements=assessments)



@app.route('/submit_formative_question_result', methods=['POST'])
def submit_formative_question_result():
    if request.method == 'POST':
        data = request.json
        student_id = current_user.user_id
        assessment_id = data.get('assessmentId')
        question_id = data.get('questionId')
        correct = data.get('correct')
        
        if data:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO Formative_Question_Results VALUES (?,?,?,?)", (student_id, assessment_id, question_id, correct))
            conn.commit()
            # Close the database connection
            conn.close()
            return 'Question Results added to database'
        else:
            return 'Invalid request', 400
        

@app.route('/submit_formative_assessment_result', methods=['POST'])
def submit_formative_assessment_result():
    if request.method == 'POST':
        print("submiting form ass res")
        data = request.json
        student_id = current_user.user_id
        assessment_id = data.get('assessmentId')
        score = data.get('score')
        max_score = data.get('maxScore')

        if data:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO Formative_Assessment_Results (Student_ID, Assessment_ID, Score, Max_Score) VALUES (?,?,?,?)", (student_id, assessment_id, score, max_score))
            conn.commit()
            # Close the database connection
            conn.close()
            return 'Assessment Results added to database'
        else:
            return 'Invalid request', 400

##############################################################################

# Function to create database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route to display existing questions
@app.route('/questions')
def questions():
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM Multiple_Choice_Questions').fetchall()
    conn.close()
    return render_template('question_index.html', questions=questions)

# Route for submitting questions
@app.route('/submit_question', methods=['POST'])
def submit_question():
    question_id = request.form.get('question_id')
    question_text = request.form['question']
    correct_answer = request.form['correct_answer']
    hint = request.form.get('hint')
    difficulty = request.form.get('difficulty')  
    options = request.form.getlist('option[]')
    tags = request.form.getlist('tag[]')

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if question_id:
            cursor.execute('''
                UPDATE Multiple_Choice_Questions
                SET Question = ?, Correct_answer = ?, Hint = ?, Difficulty = ?
                WHERE Question_ID = ?
            ''', (question_text, correct_answer, hint, difficulty, question_id))
        else:
            cursor.execute('''
                INSERT INTO Multiple_Choice_Questions (Question, Correct_answer, Hint, Difficulty)
                VALUES (?, ?, ?, ?)
            ''', (question_text, correct_answer, hint, difficulty))
            question_id = cursor.lastrowid

        cursor.execute('DELETE FROM Options WHERE Question_ID = ?', (question_id,))
        for option_text in options:
            cursor.execute('INSERT INTO Options (Question_ID, Option) VALUES (?, ?)', (question_id, option_text))

        cursor.execute('DELETE FROM Tags WHERE Question_ID = ?', (question_id,))
        for tag_text in tags:
            cursor.execute('INSERT INTO Tags (Question_ID, Tag) VALUES (?, ?)', (question_id, tag_text))

        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return "An error occurred, please try again."
    finally:
        conn.close()
    return redirect(url_for('questions'))

# Route to create new question
@app.route('/create_question')
def create_question():
    return render_template('question.html')

# Route to edit existing question
@app.route('/edit_question/<int:question_id>')
def edit_question(question_id):
    conn = get_db_connection()
    try:
        question = conn.execute('SELECT * FROM Multiple_Choice_Questions WHERE Question_ID = ?', (question_id,)).fetchone()
        options = conn.execute('SELECT Option FROM Options WHERE Question_ID = ?', (question_id,)).fetchall()
        tags = conn.execute('SELECT Tag FROM Tags WHERE Question_ID = ?', (question_id,)).fetchall()
        return render_template('question.html', question=question, options=options, tags=tags)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Route to delete existing question
@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Multiple_Choice_Questions WHERE Question_ID = ?', (question_id,))
        conn.execute('DELETE FROM Options WHERE Question_ID = ?', (question_id,))
        conn.execute('DELETE FROM Tags WHERE Question_ID = ?', (question_id,))
        conn.commit()
        return redirect(url_for('questions'))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Route to filter questions based on tags
@app.route('/filter')
def filter():
    selected_tags = request.args.getlist('tags')
    if 'apply_filter' in request.args:
        questions = get_questions_by_tags(selected_tags)
    elif 'remove_filter' in request.args:
        questions = get_questions()
    return render_template('question_index.html', questions=questions)

# Route to display a random question for answering
@app.route('/answer')
def answer():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Multiple_Choice_Questions ORDER BY RANDOM() LIMIT 1')
        question_row = cursor.fetchone()
        question_id = question_row['Question_ID']
        question = question_row['Question']
        options = conn.execute('SELECT Option FROM Options WHERE Question_ID = ?', (question_id,)).fetchall()
        correct_answer_text = question_row['Correct_answer']
        return render_template('answer.html', question=question, options=options, correct_answer_text=correct_answer_text)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


# Function to get questions filtered by selected tags
def get_questions_by_tags(tags):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = '''
            SELECT q.Question_ID, q.Question
            FROM Multiple_Choice_Questions q
            JOIN Tags t ON q.Question_ID = t.Question_ID
            WHERE t.Tag IN ({})
            GROUP BY q.Question_ID
        '''.format(','.join(['?']*len(tags)))
        cursor.execute(query, tags)
        questions = cursor.fetchall()
        return questions
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Function to get all questions from the database
def get_questions():
    conn = get_db_connection()
    try:
        questions = conn.execute('SELECT * FROM Multiple_Choice_Questions').fetchall()
        return questions
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()



# ********************************Review_RESULTS*********************************
@app.route('/results')
def results():
    if current_user.is_authenticated:
        username = current_user.username
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        if current_user.role == 'student':
            cur.execute("SELECT Student_ID FROM Students WHERE Student_Name = ?", (username,))
            student_id_row = cur.fetchone()
            student_id = student_id_row[0] 

            cur.execute("""
                SELECT a.Assessment_ID, a.Deadline, a.Assessment_Type, m.Module_Title, c.Intake_Year, ar.Score
                FROM Assessments AS a
                JOIN Modules AS m ON a.Module_ID = m.Module_ID
                JOIN Lecturers AS l ON a.Lecturer_ID = l.Lecturer_ID
                JOIN Students AS s ON l.Lecturer_ID = s.Student_ID
                JOIN Cohorts AS c ON s.Cohort_ID = c.Cohort_ID
                JOIN Assessment_Results AS ar ON a.Assessment_ID = ar.Assessment_ID
                WHERE ar.Student_ID = ?
            """, (student_id,))

            assessments = [{
                'assessment_id': row[0],
                'deadline': row[1],
                'assessment_type': row[2],
                'module_title': row[3],
                'intake_year': row[4],
                'score': row[5]
            } for row in cur.fetchall()]
            conn.close()
            return render_template('3_results_s.html', assessments=assessments)
        
        # LECTURER REVIEW
        elif current_user.role == 'lecturer':
            cur.execute("SELECT Lecturer_ID FROM Lecturers WHERE Lecturer_Name = ?", (current_user.username,))
            lecturer_id_row = cur.fetchone()
            lecturer_id = lecturer_id_row[0] if lecturer_id_row else None
            print(lecturer_id)

            # Formative assessments
            cur.execute("""
                SELECT m.Module_Title, fa.Assessment_ID, s.Intake_Year, AVG(far.Score) as Score_Avr
                FROM Formative_Assessments fa
                INNER JOIN Modules m ON fa.Module_ID = m.Module_ID
                INNER JOIN Formative_Assessment_Results far ON fa.Assessment_ID = far.Assessment_ID
                INNER JOIN Students s ON far.Student_ID = s.Student_ID
                WHERE fa.Lecturer_ID = ?
                GROUP BY fa.Assessment_ID, s.Intake_Year, m.Module_Title
                ORDER BY s.Intake_Year DESC, m.Module_Title
            """, (lecturer_id,))
            
            f_assessments = []
            for row in cur.fetchall():
                # select and make students list, using studnet_id
                cur.execute("""
                    SELECT s.Student_ID, far.Score
                    FROM Formative_Assessment_Results far
                    INNER JOIN Students s ON far.Student_ID = s.Student_ID
                    WHERE far.Assessment_ID = ?
                """, (row[1],))
                print(row)
                
                students = [{'student_id': student[0], 'score': student[1]} for student in cur.fetchall()]
                # add [students] into [assessments]
                f_assessments.append({
                    'module_title': row[0],
                    'assessment_id': row[1],
                    'intake_year': row[2],
                    'score_avr': row[3],
                    'students': students
                })
            # Summative Assessments
            # cur.execute("""
            #     SELECT m.Module_Title, sa.Assessment_ID, sa.Deadline, c.Intake_Year, AVG(sar.Score) as Score_Avr
            #     FROM Summative_Assessments sa
            #     INNER JOIN Modules m ON sa.Module_ID = m.Module_ID
            #     INNER JOIN Summative_Assessment_Results sar ON sa.Assessment_ID = sar.Assessment_ID
            #     INNER JOIN Students s ON sar.Student_ID = s.Student_ID
            #     INNER JOIN Cohorts c ON s.Cohort_ID = c.Cohort_ID
            #     WHERE sa.Lecturer_ID = ?
            #     GROUP BY sa.Assessment_ID, c.Intake_Year, m.Module_Title, sa.Deadline
            #     ORDER BY c.Intake_Year DESC, sa.Deadline ASC
            # """, (lecturer_id,))

            # s_assessments = []
            # for row in cur.fetchall():
            #     cur.execute("""
            #         SELECT s.Student_ID, sar.Score
            #         FROM Summative_Assessment_Results sar
            #         INNER JOIN Students s ON sar.Student_ID = s.Student_ID
            #         WHERE sar.Assessment_ID = ?
            #     """, (row[1],))
                
            #     students = [{'student_id': student[0], 'score': student[1]} for student in cur.fetchall()]
            #     s_assessments.append({
            #         'module_title': row[0],
            #         'assessment_id': row[1],
            #         'deadline': row[2],
            #         'intake_year': row[3],
            #         'score_avr': row[4],
            #         'students': students
            #     })

            conn.close()   
            # return render_template('4_results_l.html', f_assessments=f_assessments, s_assessments=s_assessments)
            return render_template('4_results_l.html', f_assessments=f_assessments)
    return redirect('2_login.html')


@app.route('/ass_detail_l_f/<int:assessment_id>/<int:intake_year>')
def ass_detail_l_f(assessment_id, intake_year):
    # 确认用户已认证
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # 连接数据库
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # 查询Assessments表以获取评估详情
    cur.execute("""
        SELECT m.Module_Title
        FROM Formative_Assessments a
        JOIN Modules m ON a.Module_ID = m.Module_ID
        WHERE a.Assessment_ID = ?
    """, (assessment_id,))
    assessment = cur.fetchone()

    # 如果没有找到对应的评估
    if not assessment:
        conn.close()
        return "Assessment not found", 404

    assessment_dict = {
        'module_title': assessment[0]
    }
    print(assessment_dict)

    # 获取排序参数
    sort_by = request.args.get('sort_by', 'student_id')  # 默认按Student_ID排序

    # 构造基础查询语句
    base_query = """
        SELECT s.Student_ID, s.Student_Name, ar.Score, c.Intake_Year
        FROM Students s
        JOIN Formative_Assessment_Results ar ON s.Student_ID = ar.Student_ID
        JOIN Cohorts c ON s.Cohort_ID = c.Cohort_ID
        WHERE ar.Assessment_ID = ? AND c.Intake_Year = ?
    """

    # 根据排序参数修改查询语句
    if sort_by == 'score':
        base_query += " ORDER BY ar.Score DESC"
    elif sort_by == 'name':
        base_query += " ORDER BY s.Student_Name ASC"
    else:  # 默认情况下，或者当sort_by为student_id时
        base_query += " ORDER BY s.Student_ID ASC"

    # 执行查询
    cur.execute(base_query, (assessment_id, intake_year))
    rows = cur.fetchall()

    if not rows:
        conn.close()
        return "Student not found", 404

    students = [{'student_id': row[0], 'student_name': row[1], 'score': row[2]} for row in rows]
    conn.close()

    return render_template('5_ass_detail_l.html', students=students, assessment=assessment_dict)


# ###############################################################################################################
#################################################################################################################
# Summative Assessment Section
################################################################################################################
################################################################################################################

class AddAssessmentForm(FlaskForm):
    MODULEID = SelectField('ENTER MODULE ID', coerce=int)
    deadline=DateField('Deadline for submission', format='%Y-%m-%d', validators=[DataRequired()])
    feedback = DateField('Feedbackdate', format='%Y-%m-%d', validators=[DataRequired()])
    Available = BooleanField('Available')
    st = IntegerField('Feedback timeframe', validators=[DataRequired(), NumberRange(min=1, max=2)])
    instructions=TextAreaField('Please enter key information for students', validators=[DataRequired()])
    submit = SubmitField('create assessment')
                                
conn = sqlite3.connect(DATABASE)
cur = conn.cursor()
assessmentid = cur.lastrowid 
conn.close()

@app.route("/summative_assessments_lecturer")
def summative_assessments_lecturer():
    return render_template('summative_assessments_lecturer.html')

@app.route("/activeassessments")
def activeassessments():
    activeassessments = []
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT Assessment_ID, Module_ID,Lecturer_ID, Deadline FROM Summative_Assessments_ WHERE Available = 1")
        Assessments = cur.fetchall()
        columns = [column[0] for column in cur.description]
        activeassessments = [dict(zip(columns, assessment)) for assessment in Assessments]
    except sqlite3.Error as e:
        print(f"Error is {e}")
    finally:
            conn.close()
    return render_template('activeassessments.html', activeassessments=activeassessments)


@app.route("/summative_lectureractiveassessments")
def summative_lectureractiveassessments():
    activeassessments = []
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT Assessment_ID, Module_ID,Lecturer_ID, Deadline FROM Summative_Assessments_ WHERE Available = 1")
        Assessments = cur.fetchall()
        columns = [column[0] for column in cur.description]
        activeassessments = [dict(zip(columns, assessment)) for assessment in Assessments]
    except sqlite3.Error as e:
        print(f"Error is {e}")
    finally:
            conn.close()
    return render_template('summative_lectureractiveassessments.html', activeassessments=activeassessments)



@app.route("/summative_inactiveactiveassessments")
def summative_inactiveactiveassessments():
    inactiveassessments = []
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT Assessment_ID, Module_ID,Lecturer_ID, Deadline FROM Summative_Assessments_ WHERE Available = 0")
        Assessments = cur.fetchall()
        columns = [column[0] for column in cur.description]
        inactiveassessments = [dict(zip(columns, assessment)) for assessment in Assessments]
    except sqlite3.Error as e:
        print(f"Error is {e}")
    finally:
            conn.close()
    return render_template('summative_inactiveactiveassessments.html', inactiveassessments=inactiveassessments)

@app.route("/summative_createassessment", methods=['GET', 'POST'])
def summative_createassessment():
    lecturerid = session['lecturer_id']
    lecturerid = lecturerid[0]
    form = AddAssessmentForm()
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("Select Module_ID, Module_Title from Modules")
    modules=cur.fetchall()
    conn.close()
    form.MODULEID.choices = [(m['Module_ID'], m['Module_Title']) for m in modules]
    if form.validate_on_submit():
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO Summative_Assessments_ (Module_ID, Lecturer_ID,  Deadline, Feedbackdate, Available, Feedbacktype, Instructions) VALUES (?,?,?,?,?,?,?)", ( form.MODULEID.data, lecturerid, form.deadline.data,form.feedback.data,  form.Available.data,  form.st.data, form.instructions.data ))                                                                                          
            conn.commit()
            assessmentid = cur.lastrowid 
            flash("hugesuccess!")
            if assessmentid:
                return redirect(url_for('summative_addassessmentquestions', assessmentid=assessmentid))
            else: 
                return (f"there is no assessment id")
        except sqlite3.Error as e:
            print(f"Error is {e}")
            return (f"this is not supposed to happen")
        finally:
            conn.close()
    else:
         print(form.errors)
    return render_template('summative_createassessment.html', form=form)

# warning assignment page 
@app.route("/summative_deleteassessment/<int:assessmentid>")
def summative_deleteassessment(assessmentid):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM Summative_Assessments_ WHERE Assessment_ID = ?", (assessmentid,))
        conn.commit()
        flash("successful deletion of assessment")
    except sqlite3.Error as e:
            print(f"Error is {e}")
            return (f"this is not supposed to happen")
    finally:
            conn.close()
    return redirect(url_for('summative_lectureractiveassessments'))


# warning page
@app.route("/lecturerexamwarning")
def lecturerwarning():
    return render_template('lecturerexamwarning.html')
    
@app.route("/editassignmentquestions/<int:assessmentid>", methods=['GET', 'POST'])
def editassignmentquestions(assessmentid):
    try: 
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT Questions.Question_ID, Questions.Question, Questions.Hint, Questions.Topic, Questions.Answer, Summative_Assessment_Questions_.Assessment_ID 
            FROM Questions
            LEFT JOIN
            Summative_Assessment_Questions_ ON Questions.Question_ID = Summative_Assessment_Questions_.Question_id
            AND Summative_Assessment_Questions_.Assessment_id = ?""", (assessmentid,))
        questions = cur.fetchall()
        if questions:
            return render_template("editassignmentquestions.html", questions=questions, assessmentid=assessmentid)
        else:
            return render_template("lecturerexamwarning.html")
    except sqlite3.Error as e:
        print(f"Error is {e}")
        return "uh oh"
    finally:
         conn.close()

# completed with new route
@app.route("/summative_addassessmentquestions/<int:assessmentid>", methods=['GET', 'POST'])
def summative_addassessmentquestions(assessmentid):
    try: 
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT Multiple_Choice_Questions.Question_ID, Options.Option, Summative_Assessment_Questions_.Assessment_ID, Multiple_Choice_Questions.Question, Multiple_Choice_Questions.Hint, Multiple_Choice_Questions.Correct_answer
            FROM Multiple_Choice_Questions
            JOIN
            Summative_Assessment_Questions_ ON Multiple_Choice_Questions.Question_ID = Summative_Assessment_Questions_.Question_id
            Join Options ON Multiple_Choice_Questions.Question_ID = Options.Question_ID
            AND Summative_Assessment_Questions_.Assessment_id = ?""", (assessmentid,))
        questionsall = cur.fetchall()
        questions = {}
        for question in questionsall:
            question_id = question['Question_ID']
            if question_id not in questions:
                        # question = questions['Question']
                        # options = cur.execute('SELECT Option FROM Options WHERE Question_ID = ?' (question_id,)).fetchall()
                            questions[question_id] = {
                                'Question_ID' : question['Question_ID'],
                                'Question' : question['Question'],
                                'Assessment_ID' : question['Assessment_id'],
                                'Hint' : question['Hint'],
                                'Options' : [],
                                'Correct_answer' : question['Correct_answer'] 
                            }
            questions[question_id]['Options'].append(question['Option'])
        questionsend = list(questions.values())

        cur.execute(  """SELECT Multiple_Choice_Questions.Question_ID, Options.Option,  Multiple_Choice_Questions.Question, Multiple_Choice_Questions.Hint, Multiple_Choice_Questions.Correct_answer
            FROM Multiple_Choice_Questions
            Join Options ON Multiple_Choice_Questions.Question_ID = Options.Question_ID
            """)
        questionsall2 = cur.fetchall()
        questions2 = {}
        for q in questionsall2:
                question_id = q['Question_ID']
                if question_id not in questions2:
                            # question = questions['Question']
                            # options = cur.execute('SELECT Option FROM Options WHERE Question_ID = ?' (question_id,)).fetchall()
                                questions2[question_id] = {
                                    'Question_ID' : q['Question_ID'],
                                    'Question' : q['Question'],
                                    'Hint' : q['Hint'],
                                    'Options' : [],
                                    'Correct_answer' : q['Correct_answer'] 
                                }
                questions2[question_id]['Options'].append(q['Option'])
        questionsend2 = list(questions2.values())
        print("questions2", questionsend2)
        print("questions1",questionsend)
            
        return render_template("summative_addassessmentquestions.html", questions=questionsend, question2=questionsend2, assessmentid=assessmentid)
    except sqlite3.Error as e:
        print(f"Error is {e}")
        return "uh oh"
    finally:
            conn.close()

@app.route('/qa', methods=['GET','POST'])
def qa():
    if request.method == 'POST':
        Question_id = int(request.form['qid'])
        assessmentid = int(request.form['assessmentid'])
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("INSERT INTO Summative_Assessment_Questions_ (Assessment_ID, Question_ID) VALUES (?, ?)", (assessmentid, Question_id))
            conn.commit()
            flash("successfully added questions")
        except sqlite3.Error as e:
            print(f"Error is {e}")
            return (f"uh oh")
        finally:
            conn.close()
        return redirect(url_for("summative_addassessmentquestions", assessmentid=assessmentid))
    else:
        return render_template("summative_addassessmentquestions.html", assessmentid=assessmentid)

@app.route('/qd', methods=['GET','POST'])
def qd():
    if request.method == 'POST':
        Question_id = int(request.form['qid'])
        assessmentid = int(request.form['assessmentid'])
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("DELETE FROM Summative_Assessment_Questions_ WHERE Assessment_ID = ? AND Question_ID = ?", (assessmentid, Question_id))
            conn.commit()
            flash("successfully deleted questions")
        except sqlite3.Error as e:
            print(f"Error is {e}")
            return (f"uh oh")
        finally:
            conn.close()
        return redirect(url_for("summative_addassessmentquestions", assessmentid=assessmentid))
    else:
        return render_template("summative_addassessmentquestions.html", assessmentid=assessmentid)







# format student exam output into buttons
@app.route("/summative_assessments_student")
def summative_assessments_student():
    Studentassessments = []
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT Assessment_ID, Module_ID,Lecturer_ID, Deadline FROM Summative_Assessments_ WHERE Available = 1")
        Assessments = cur.fetchall()
        columns = [column[0] for column in cur.description]
        Studentassessments = [dict(zip(columns, assessment)) for assessment in Assessments]
    except sqlite3.Error as e:
        print(f"Error is {e}")
    finally:
            conn.close()
    return render_template('summative_assessments_student.html', Studentassessments=Studentassessments)


@app.route("/summative_studentassessmentdetails/<int:assess>")
def summative_studentassessmentdetails(assess):
    try: 
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT Assessment_ID, Module_ID, Lecturer_ID, Deadline, Feedbackdate, Feedbacktype, Instructions From Summative_Assessments_ Where Assessment_ID = ?", (int(assess),))
        details = cur.fetchone()
        if details:
            return render_template("summative_studentassessmentdetails.html", details=details)
        else:
            return render_template("lecturerexamwarning.html")
    except sqlite3.Error as e:
        print(f"Error is {e}")
        return "uh oh"
    finally:
            conn.close()


@app.route("/summative_studentexaminprogress/<int:Taketest>/<int:scoringtype>")
def summative_studentexaminprogress(Taketest, scoringtype):
     try: 
        assessmentid = Taketest
        scoringtype = scoringtype
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT Multiple_Choice_Questions.Question, Multiple_Choice_Questions.Question_ID, Multiple_Choice_Questions.Hint, Options.Option, Multiple_Choice_Questions.Correct_Answer
            From Multiple_Choice_Questions
            Join Summative_Assessment_Questions_ ON Multiple_Choice_Questions.Question_ID = Summative_Assessment_Questions_.Question_ID
            Join Options ON Multiple_Choice_Questions.Question_ID = Options.Question_ID
            Where Summative_Assessment_Questions_.Assessment_ID = ?""", (int(Taketest),))
        questionstotal = {}
        questions = cur.fetchall()
        for question in questions:
            print(questions)
            question_id = question['Question_ID']
            if question_id not in questionstotal:
            # question = questions['Question']
            # options = cur.execute('SELECT Option FROM Options WHERE Question_ID = ?' (question_id,)).fetchall()
                questionstotal[question_id] = {
                    'Question_ID' : question['Question_ID'],
                    'Question' : question['Question'],
                    'Hint' : question['Hint'],
                    'Options' : [],
                    'Correct_answer' : question['Correct_answer'] 
                }
            correct_answer_text = question['Correct_answer']
            questionstotal[question_id]['Options'].append(question['Option'])
            questionsend = list(questionstotal.values())
            print(f"Question ID {question_id} , Option : {question['Option']}")
        if questionsend:
            return render_template("summative_studentexaminprogress.html", correct_answer_text=correct_answer_text, questions=questionsend, assessmentid=Taketest, scoringtype=scoringtype)
        else:
            return render_template("lecturerexamwarning.html")
     except sqlite3.Error as e:
        print(f"Error is {e}")
        return "uh ohh"
     finally:
            conn.close()


@app.route('/scoring', methods=['POST'])
def recievescore():
     data = request.get_json()
     score = data['score']
     total = data['Total']
     assessmentid = data['assessmentid']
     conn = sqlite3.connect(DATABASE)
     cur = conn.cursor()
     studentid = session['student_id']
     studentid = studentid[0]
     print(studentid)
     try:
        cur.execute("INSERT INTO Summative_Results_ (Score, Max_Score ,Assessment_ID, student_id) VALUES (?,?,?,?)",(score,total,assessmentid,studentid))
        conn.commit()
        return({'message':'Score saved'})
     except sqlite3.Error as e:
        print(f"Error is {e}")
        return jsonify({'error : {e}'})
     except Exception as e:
        print(f"Error is {e}")
        return jsonify({'500 error : {e}'})
     finally:
        conn.close()

@app.route("/warningbeforesubmission")
def warningbeforesubmission():
    return render_template('warningbeforesubmission.html')


# student result
@app.route('/student_results')
@login_required
def student_results():
    if current_user.role == 'student':
        username = current_user.username
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Ensure that rows are returned as dictionaries
        cur = conn.cursor()
        cur.execute("SELECT Student_ID FROM Students WHERE Student_Name = ?", (username,))
        student_info = cur.fetchone()
        if student_info:
            student_id = student_info['Student_ID']  # Access by column name
            cur.execute("""
                SELECT fa.Title, fa.Assessment_ID, COUNT(faq.Question_ID) AS No_Of_Questions, far.Score, far.Max_Score
                FROM Formative_Assessments fa
                LEFT JOIN Formative_Assessment_Results far ON fa.Assessment_ID = far.Assessment_ID
                LEFT JOIN Formative_Assessment_Questions faq ON fa.Assessment_ID = faq.Assessment_ID
                WHERE far.Student_ID = ?
                GROUP BY fa.Assessment_ID
            """, (student_id,))
            formative_assessments = cur.fetchall()
            print("Queried Data:")  
            for row in formative_assessments:
                print(dict(row))  # 将Row对象转换为字典并打印
            return render_template('3_results_s.html', formative_assessments=formative_assessments)
        else:
            flash('No student information found.')
        conn.close()
    return redirect(url_for('home'))


# student detail
@app.route('/student/detail/<int:assessment_id>')
@login_required
def student_detail(assessment_id):
    if current_user.role == 'student':
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

         # student_id = get_student_id(current_user.username)
        username = current_user.username
        cur.execute("SELECT Student_ID FROM Students WHERE Student_Name = ?", (username,))
        student_id_row = cur.fetchone()
        student_id = student_id_row[0] 
        print(student_id)


        # 获取评估信息
        cur.execute("""
            SELECT Title, Instructions, Difficulty, No_Of_Questions, Available
            FROM Formative_Assessments
            WHERE Assessment_ID = ?
        """, (assessment_id,))
        assessment_info = cur.fetchone()
        assessment = dict(assessment_info)
        print(assessment)

        # 获取问题详细信息
        cur.execute("""
            SELECT fqr.Question_ID, fqr.Correct, mcq.Question, mcq.Correct_Answer
            FROM Formative_Question_Results fqr
            JOIN Multiple_Choice_Questions mcq ON fqr.Question_ID = mcq.Question_ID
            WHERE fqr.Assessment_ID = ? AND fqr.Student_ID = ?
            ORDER BY fqr.Question_ID
        """, (assessment_id, student_id))
        questions = [{'Question_ID': row[0], 'Correct': row[1], 'Question': row[2], 'Correct_Answer': row[3]} for row in cur.fetchall()]
        print(questions)
        print(len(questions))

        # 确保关闭数据库连接
        conn.close()

        return render_template('6_ass_detail_s.html', 
                        assessment=assessment, questions=questions
                        )


@app.route('/test_db')
def test_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM some_table")
    count = cur.fetchone()[0]
    conn.close()
    return f"Number of records in 'some_table': {count}"

    
if __name__ == '__main__':
    app.run(debug=True)