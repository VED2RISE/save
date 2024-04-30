function addQuestion(question) {
    // Clone the unadded question div
    let addedQuestion = question.cloneNode(true);
    addedQuestion.className = "card border-dark mb-3 added-qstn"; // Change classname to added
    let button = addedQuestion.querySelector('.add-question-btn');  
    button.textContent = "Remove"; // Change button Text and Classname
    button.className = "btn btn-secondary remove-question-btn";
    document.querySelector('.added-questions').append(addedQuestion); // Add to added qs div

    button.addEventListener('click', function() {
        const parentElement = this.parentElement;
        removeQuestion(parentElement); // add remove Q event listener
    })
    let addedQuestionID = button.parentElement.querySelector('.added-questions .question-id').textContent;
    addQuestionToSession(addedQuestionID); // Get ID and add to session
}
// Remove Questions from front-end and call to be removed from session
function removeQuestion(question) {
    const questionId = question.querySelector('.question-id').textContent;
    document.querySelector('.added-questions').removeChild(question);
    removeQuestionFromSession(questionId);
} 

// Function to add question IDs to session
function addQuestionToSession(questionId) {
    // Send an AJAX request to Flask route to add question ID to session
    fetch('/add_question_to_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ questionId: questionId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Question ID added to session');
    })
    .catch(error => {
        console.error('Error adding question ID to session:', error);
    });
}

// Function to remove question IDs to session
function removeQuestionFromSession(questionId) {
    // Send an AJAX request to Flask route to remove question ID to session
    fetch('/remove_question_from_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ questionId: questionId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Question ID removed to session');
    })
    .catch(error => {
        console.error('Error adding question ID to session:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Add function to add question buttons
    const buttons = document.querySelectorAll('.add-question-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const parentElement = this.parentElement;
            addQuestion(parentElement);
    });
});
});

/// Add event listener function to allow removal of questions loaded in the added questions field through session
document.addEventListener('DOMContentLoaded', function() {
    // Add function to add question buttons
    const rmv_buttons = document.querySelectorAll('.remove-question-btn');
    rmv_buttons.forEach(button => {
        button.addEventListener('click', function() {
            const parentElement = this.parentElement;
            removeQuestion(parentElement);
    });
});
});

function deleteWarning() {
    const hiddenWarning = document.querySelector('.delete-assessment-msg');
    hiddenWarning.style.display = "block";
    const deleteBtn = document.querySelector('.delete-assessment-btn-first');
    deleteBtn.style.display = 'none';

}

function hideWarning() {
    const warning = document.querySelector('.delete-assessment-msg');
    warning.style.display = "none";
    const deleteBtn = document.querySelector('.delete-assessment-btn-first');
    deleteBtn.style.display = 'block';

}

tags = []
document.addEventListener('DOMContentLoaded', function () {
// Get all option elements with class "tag-option"
const options = document.querySelectorAll('.tag-option');

// Add click event listener to each option
options.forEach(option => {
    option.addEventListener('click', function() {
        // Add tag Id to the session
        const tagId = option.dataset.tagId;

        console.log(tags)
        // Stop it from adding multiple of the same tag
        if (tags.includes(tagId)) {
            return 0;
        }
        tags.push(tagId)
        addTagToSession(tagId);
        // Now you can use the tagId as needed

        // Create a new list item
        var listItem = document.createElement("li");
        listItem.textContent = option.textContent;

        // Create a delete button
        var deleteButton = document.createElement("button");
        deleteButton.textContent = "X";
        deleteButton.classList.add("btn", "btn-danger", "btn-sm");
        deleteButton.onclick = function() {
            listItem.remove();
            // Create new copy of the array without the given tagId
            tags = tags.filter(function(id) {
                return id !== tagId;
            });
            removeTagFromSession(tagId);
        };

        // Append delete button to list item
        listItem.appendChild(deleteButton);

        // Append list item to selected tags list
        var selectedTagsList = document.getElementById("selectedTags");
        selectedTagsList.appendChild(listItem);

       
    });
});
});


// Function to add tag to session 
function addTagToSession(tagId) {
    // Send an AJAX request to Flask route to add question ID to session
    fetch('/add_tag_to_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tagId : tagId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Tag ID added to session');
    })
    .catch(error => {
        console.error('Error adding tag ID to session:', error);
    });
}

// Function to removetag IDs to session
function removeTagFromSession(tagId) {
    // Send an AJAX request to Flask route to remove tag ID to session
    fetch('/remove_tag_from_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tagId: tagId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('tag ID removed to session');
    })
    .catch(error => {
        console.error('Error adding tag ID to session:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    tagFormBtns = document.querySelectorAll('.tags-btn-submit');
    tagFormBtns.forEach(button => {
        button.addEventListener('click', function(){
            tags = [];
        });
});
});
