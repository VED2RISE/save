import sqlite3
from flask import Flask, jsonify, flash, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, IntegerField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import Flask, flash, render_template, request, session, redirect, request, session
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from jinja2 import Environment

import json
import sqlite3

# UPDATE ALL HOME ROUTES TO HOME-LUKE
app = Flask(__name__)
DATABASE = 'upGradeDB.db'

# needed for do statement on add assignment questions
environment = Environment(extensions=['jinja2.ext.do'])
app.jinja_env.add_extension('jinja2.ext.do')

app.config['SECRET_KEY'] = "super secret key"

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
# LOGIN

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


integer_choices = [(1, 1), (2, 2), (3,3), (4,4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10,10), (11,11), (12,12)]
available_choices = [(1, "Yes"), (2, "No")]
difficulty_choices = [("Beginner"), ("Intermediate"), ("Advanced")]
module_choices = [(119, "Computational Thinking"), (120, "Fundamentals of Programming"),(313, "Software Engineering")]
tags = [(1, "JavaScript"), (2, "Python"), (3, "Java")]
# MY CODE:
#summative_lectureractiveassessments


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


# edited for toms bit
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

# COMPLETE SQL TABLE CHANGE AND QUERY 



@app.route("/warningbeforesubmission")
def warningbeforesubmission():
    return render_template('warningbeforesubmission.html')
    
    
if __name__ =="__main__":
    app.run(debug=True)

