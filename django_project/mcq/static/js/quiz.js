// ------------------------------------------------------------------------------------------------
function checkAnswer(question_id) {
    let answerInput = document.querySelector(`input[name="answer-${question_id}"]`);
    let answerValue = answerInput.value;
    let answerIDs = answerValue.split(",");
    let selectedChoiceIDs = [];
    let inputElements = document.querySelectorAll(`input[name="choice_id-${question_id}"]`);
    for (let i = 0; i < inputElements.length; i++) {
        let inputElement = inputElements[i];
        if (inputElement.checked) {
            selectedChoiceIDs.push(inputElement.value);
        }
    }
    let answerCompared = JSON.stringify(answerIDs) === JSON.stringify(selectedChoiceIDs);
    const explanationRow = document.getElementById(`explanation-${question_id}`);
    const questionButton = document.getElementById(`button-${question_id}`);
    const checkButton = document.getElementById(`check-${question_id}`);
    const checkButtons = document.querySelectorAll(`[id^="check-"]`);
    const totalCheckButtons = checkButtons.length;

    if (questionButton.classList.contains("btn-outline-dark") && !checkButton.disabled) {        
        if (answerCompared) {
            checkButton.disabled = true;
            checkButton.classList.replace("btn-outline-dark", "btn-secondary");
            explanationRow.style.display = "table-row";
            explanationRow.querySelector(".btn-fa-check").style.display = "inline-block";
            explanationRow.querySelector(".btn-fa-xmark").style.display = "none";
            questionButton.classList.replace("btn-outline-dark", "btn-success");
            let scoreElement = document.getElementById("score");
            let currentScore = parseInt(scoreElement.innerText);
            scoreElement.innerText = currentScore + 1;
            let markElement = document.getElementById("mark");
            let currentMark = Math.round(parseInt(scoreElement.innerText /totalCheckButtons * 100))
            markElement.innerText = currentMark;
        

        } else {
            checkButton.disabled = true;
            checkButton.classList.replace("btn-outline-dark", "btn-secondary");
            explanationRow.style.display = "table-row";
            explanationRow.querySelector(".btn-fa-check").style.display = "none";
            explanationRow.querySelector(".btn-fa-xmark").style.display = "inline-block";
            questionButton.classList.replace("btn-outline-dark", "btn-danger");
            for (let i = 0; i < inputElements.length; i++) {
                inputElements[i].checked = false;
                if (answerIDs.includes(inputElements[i].value)) {
                    inputElements[i].checked = true;
                    inputElements[i].parentNode.classList.add("correct-answer");
                }
            }
        }
    }
}
// ------------------------------------------------------------------------------------------------
function jumpToQuestion(question_id) {
    location.href = "#question-" + question_id;
}
