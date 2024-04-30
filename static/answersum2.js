
function submitAnswers() {
    var questioncontainers = document.querySelectorAll('.answer-container');
    var score = 0;
    var total = questioncontainers.length;
    // below may cause issues
    var assessmentid = document.getElementById('assessmentid').value
    questioncontainers.forEach(q => {
        var questionid = q.querySelector('input[type="hidden"').id.replace('correct_answer_text_','');
        var selectedOption = q.querySelector('input[name="selected_option_' + questionid +'"]:checked');
        var correctAnswerText = document.getElementById('correct_answer_text_' + questionid).value;
        var feedbackDiv = document.getElementById("feedback_" + questionid);
    
   
    if (!selectedOption) {
        alert("Please select an option." + questionid + ".");
        return;
    }
    if (selectedOption.value.trim() == correctAnswerText) {
        score+=1;
        console.log(score)
        
    } else {
    }
    feedbackDiv.style.display = "block";
    
    })
console.log("your score is " + score + "out of " + total);
document.getElementById('submitbutton').style.display = 'none';
var msg = document.getElementById('postsubmissionmsg');
msg.innerHTML = "<h4>Thank you for submitting your answers, you will recieve your score on as specified in the information section";
msg.style.display = 'block';

sendscore(score,total, assessmentid)

}

function sendscore(score, total, assessmentid){
    fetch('/scoring',{
        method : 'POST',
        headers: {
            'Content-Type' : 'application/json',
        },
        body : JSON.stringify({ score: score, Total : total, assessmentid : assessmentid })
    })
        .then(response => response.json())
        .then(data => console.log('data recieved:', data))
        .catch((error) => {
            console.error('Error has occurred:', error);
        })
    }
