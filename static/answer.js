const answers = document.querySelectorAll('.answer-container') // Get the question-answer-container
const submitFinalButton = document.querySelector('.submit-assessment-btn') // Get the submit button
let assessmentId;

document.addEventListener('DOMContentLoaded', function() {

    document.getElementById("assessmentForm").addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent default form submission behavior
    });

    submitFinalButton.addEventListener('click', function assessmentQuestionChecker() {
        let score = 0;
        let maxScore = answers.length;
        const assessment = document.getElementById("assessmentForm");
        assessmentId = assessment.dataset.assessmentId;
    
        let mark_sheet = []; // list of objects to [{questionId:id, complete:t/f, correct:t/f}]
        
        answers.forEach((answer) => mark_sheet.push( checkAnswer(answer) ) );
    
        
        for (let i = 0 ; i < mark_sheet.length ; i++ ) {
            if (!mark_sheet[i].complete) {
                return "Question incomplete"
            }
        }
        // answers.forEach((answer) => score += checkAnswer(answer,complete)); // Check each answer
        for (let i = 0 ; i < mark_sheet.length ; i++ ) {
            submitQuestionResult(assessmentId, mark_sheet[i].questionId, mark_sheet[i].correct);
            if (mark_sheet[i].correct) { 
                score++ };
        }
        console.log(score);
        submitAssessmentResult(assessmentId, score, maxScore);
        let msg = `Score: ${score}/${maxScore}`;
        let msgP = document.querySelector('.res-msg');
        msgP.textContent = msg;

        const tryAgainBtn = document.querySelector('#try-again-btn');
        tryAgainBtn.style.display = 'block';

    });
})




function checkAnswer(answer) {

    let correct = false;
    // Get the selected option within the answer container
    const selectedOption = answer.querySelector('.selected_option:checked');
    if (!selectedOption) {
        alert("Please select an option."); // alert if not selected
        return {'complete': false};
    }
    const correctAnswerText = answer.querySelector('.correct-answer').value;
    let feedbackDiv = answer.querySelector('.feedback');
    if (selectedOption.nextSibling.textContent.trim() == correctAnswerText) {
        feedbackDiv.innerHTML = "<p style='color:green;'>Correct!</p>";
        correct = true;
        
    } else {
        feedbackDiv.innerHTML = "<p style='color:red;'>Incorrect. Try again.</p>";
    }
    feedbackDiv.style.display = "block";

    // Get question and assessment Id data
    const questionId = selectedOption.dataset.questionId;
    
    // submitQuestionResult(assessmentId, questionId, correct);

    
    return {'questionId': questionId, 'complete': true, 'correct': correct};

}

// Need to submit an entry for each question into Formative_Assessment_Question_Results
// StudentId, AssessmentId, QuestionId, Correct
function submitQuestionResult(assessmentId, questionId, correct){
    // Send an AJAX request to Flask route to submit question result
    fetch('/submit_formative_question_result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ assessmentId:assessmentId,
                                questionId: questionId,
                                correct: correct })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Question results sent to server');
    })
    .catch(error => {
        console.error('Error sending question results to server:', error);
    });

}

function submitAssessmentResult(assessmentId, score, maxScore){
    fetch('/submit_formative_assessment_result', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ assessmentId:assessmentId,
                                score: score,
                                maxScore: maxScore                                 })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Assessment result sent to server');
    })
    .catch(error => {
        console.error('Error sending assessment result to server:', error);
    });
}