//TODO:
/*
    Add more questions
    If answer is incorrect, show the correct answer
    Create an endpoint for when a user reaches a score
    Figure out points to be given to the user through database
    Clear code and remove any console.log
*/

import Ball from './Ball.js';
import Paddle from './Paddle.js';

const ball = new Ball(document.getElementById("ball"));
const playerPaddle = new Paddle(document.getElementById("player-paddle"));
const computerPaddle = new Paddle(document.getElementById("computer-paddle"));
const playerScoreElem = document.getElementById("player-score");
const computerScoreElem = document.getElementById("computer-score");
const modal = document.querySelector('#modal');
const closeModal = document.querySelector('.close-button');
const answers = document.getElementById('answers')
const title = document.getElementById("title");
const question = document.getElementById("question");
const options = document.querySelectorAll('option');
const optionA = document.getElementById("option-one-label");
const optionB = document.getElementById("option-two-label");
const optionC = document.getElementById("option-three-label");
const optionD = document.getElementById("option-four-label");
const closeBtn = document.getElementById("close")

const questions = [
    {
        question: "What should you do if you see someone being bullied online?",
        optionA: "Report it",
        optionB: "Ignore it",
        optionC: "Join in",
        optionD: "Just watch",
        correctOption: "optionA"
    },
    {
        question: "How many children have experienced cyberbullying before?",
        optionA: "92%",
        optionB: "76%",
        optionC: "84%", 
        optionD: "68%",
        correctOption: "optionC"
    },
    {
        question: "How many percent of children have been online at some point?",
        optionA: "100%",
        optionB: "99%",
        optionC: "94%",
        optionD: "96%",
        correctOption: "optionB"
    }
];

// Game variables
let lastTime;
let playing = false;

// Quiz variables
let shuffledQuestions = [];
let questionNumber = 0;
let score = 0;

title.innerHTML = "Welcome!"
question.innerHTML = "Play pong and after every point, you will be asked a question.<br>You will be awarded points if you get the question correct.<br>The quicker you answer it correctly, the more points you'll get."
closeBtn.innerHTML = "Start"
answers.style.display="none"
console.log(questionNumber)
console.log(score)
modal.showModal();

function update(time) {
    if (lastTime != null) {
        const delta = time - lastTime;
        ball.update(delta, [playerPaddle.rect(), computerPaddle.rect()]);
        computerPaddle.update(delta, ball.y);
        const hue = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--hue"));

        document.documentElement.style.setProperty("--hue", hue + delta * 0.01);
    }

    if (isLose()) {
        handleLose();
        window.requestAnimationFrame(pause);
    } else {    
        lastTime = time;
        window.requestAnimationFrame(update);
    }
}

function pause(time) {
    if (lastTime != null) {
        const delta = time - lastTime;
        const hue = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--hue"));

        document.documentElement.style.setProperty("--hue", hue + delta * 0.01);
    }
    if (playing == true) {
        window.requestAnimationFrame(update);
    } else {
        lastTime = time;
        window.requestAnimationFrame(pause);
    }
}

function isLose() {
    const rect = ball.rect();
    return rect.right >= window.innerWidth || rect.left <= 0;
}

closeModal.addEventListener('click', () => {
    modal.close();
    playing = true;
})

document.getElementById('submitBtn').onclick = function() {
    console.log("Button clicked")
    const currentQuestion = shuffledQuestions[questionNumber];
    const currentQuestionAnswer = currentQuestion.correctOption;
    console.log(currentQuestionAnswer)


    const answer = getSelected()
    console.log("currentQuestionAnswer: " + currentQuestionAnswer)
    if (answer === currentQuestionAnswer) {
        score++
        question.innerHTML = "Score: " + score
        answers.style.display="none"
        console.log("Correct")
        title.innerHTML = "Correct!"
    } else {
        question.innerHTML = "Score: " + score
        answers.style.display="none"
        console.log("Incorrect")
        title.innerHTML = "Incorrect!"
    }
    closeBtn.style.display = "block"
    closeBtn.innerHTML = "Continue"
    console.log(score)
    ball.reset();
    computerPaddle.reset();
    questionNumber++
    // window.requestAnimationFrame(update)
}

function getSelected() {
    let answer
    let selected = document.querySelector('input[name="option"]:checked') 
    console.log("selected: " + selected.value)
    
    console.log("Answer: " + answer)
    return selected.value
}

function handleLose() {
    playing = false;
    const rect = ball.rect();
    if (rect.right >= window.innerWidth) {
        playerScoreElem.textContent = parseInt(playerScoreElem.textContent) + 1;
    } else {
        computerScoreElem.textContent = parseInt(computerScoreElem.textContent) + 1;
    }
    //TODO:
        // Pick random number
        // Select the question from the selected list and the corresponding answer
        // Set the innerHTML title, question and answers
    const currentQuestion = shuffledQuestions[questionNumber];
    console.log(questionNumber)
    title.innerHTML = "New question";
    question.innerHTML = currentQuestion.question;
    optionA.innerHTML = currentQuestion.optionA;
    optionB.innerHTML = currentQuestion.optionB;
    optionC.innerHTML = currentQuestion.optionC;
    optionD.innerHTML = currentQuestion.optionD;
    answers.style.display = "block"
    closeBtn.style.display = "none"
        // Show the modal
        // Need to sort the submit button - currently restarts the webpage
    modal.showModal(); // Pop up question for the answer
}

function handleQuestions() {
    while (shuffledQuestions.length <= 2) {
        const random = questions[Math.floor(Math.random() * questions.length)]
        if (!shuffledQuestions.includes(random)) {
            shuffledQuestions.push(random);
        }
    }
}

document.addEventListener("mousemove", e =>  {
    playerPaddle.position = (e.y / window.innerHeight) * 100;
})

handleQuestions();
window.requestAnimationFrame(pause);