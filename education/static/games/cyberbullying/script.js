//TODO:
/*
    Add more questions
    If the user gets a question right, add an advantage
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
const countdown = document.getElementById("countdown")
const question = document.getElementById("question");
const options = document.querySelectorAll('option');
const optionA = document.getElementById("option-one-label");
const optionB = document.getElementById("option-two-label");
const optionC = document.getElementById("option-three-label");
const optionD = document.getElementById("option-four-label");
const closeBtn = document.getElementById("close")
const homeBtn = document.getElementById("home")
const dbPoints = document.getElementById("dbPoints")

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
let timer;
let timeDisplay;
let timerRun;
let startTime;
let endTime;

// Quiz variables
let shuffledQuestions = [];
let questionNumber = 0;
let score = 0;
let totalPoints = 0;

title.innerHTML = "Welcome!"
question.innerHTML = "Play pong and after every point, you will be asked a question.<br>You will be awarded points if you get the question correct.<br>The quicker you answer it correctly, the more points you'll get."
closeBtn.innerHTML = "Start"
countdown.style.display = "none"
answers.style.display="none"
homeBtn.style.display="none"
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

document.getElementById('submitBtn').onclick = function checkAnswer() {
    timerRun = false;
    let d2 = new Date();
    endTime = d2.getTime();
    const timeTaken = endTime - startTime;
    clearTimeout(timer);
    const currentQuestion = shuffledQuestions[questionNumber];
    const currentQuestionAnswer = currentQuestion.correctOption;

    const answer = getSelected();
    if (answer === currentQuestionAnswer) {
        score++;
        // points = totalTime / timeTaken (in ms)
        let points = Math.round(30000 / timeTaken) * 3;
        // dbPoints += points;
        totalPoints += points
        dbPoints.value = totalPoints
        console.log(dbPoints)
        
        question.innerHTML = "Score: " + score;
        answers.style.display="none";
        title.innerHTML = "Correct!";
        countdown.style.display = "none";
    } else {
        let ans;
        for (let i=0; i < answers.length; i++) {
            if (answers[i].value == currentQuestionAnswer) {
                ans = answers[i];
            }
        }
        let ansValue = ans.value;
        title.innerHTML = "Incorrect!"
        question.innerHTML = "The correct answer was: " + currentQuestion[ansValue] + "<br>Score: " + score
        answers.style.display="none"
        countdown.style.display = "none"
    }
    closeBtn.style.display = "block"
    closeBtn.innerHTML = "Continue"
    ball.reset();
    computerPaddle.reset();
    questionNumber++
    // window.requestAnimationFrame(update)
}

function endGame() {
    question.innerHTML = "Your points will be added to your profile and you will be taken back to the home page!"
    title.innerHTML = "Game has finished!"
    closeBtn.style.display = "none"
    homeBtn.style.display = "block"
    modal.showModal()
}

function getSelected() {
    let selected = document.querySelector('input[name="option"]:checked') 
    return selected.value
}

function noAnswer() {
    timerRun = false;
    modal.close()
    const currentQuestion = shuffledQuestions[questionNumber];
    const currentQuestionAnswer = currentQuestion.correctOption;

    title.innerHTML = "You ran out of time!"
    question.innerHTML = "The correct answer was: " + currentQuestionAnswer + "<br>Score: " + score
    answers.style.display="none"
    closeBtn.style.display = "block"
    closeBtn.innerHTML = "Continue"
    countdown.style.display = "none"

    modal.show()

    ball.reset();
    computerPaddle.reset();
    questionNumber++
}

function handleLose() {
    playing = false;
    const rect = ball.rect();
    if (rect.right >= window.innerWidth) {
        playerScoreElem.textContent = parseInt(playerScoreElem.textContent) + 1;
    } else {
        computerScoreElem.textContent = parseInt(computerScoreElem.textContent) + 1;
    }

    title.innerHTML = "New question";
    if (questionNumber == shuffledQuestions.length) { endGame() }

    const currentQuestion = shuffledQuestions[questionNumber];
    question.innerHTML = currentQuestion.question;
    optionA.innerHTML = currentQuestion.optionA;
    optionB.innerHTML = currentQuestion.optionB;
    optionC.innerHTML = currentQuestion.optionC;
    optionD.innerHTML = currentQuestion.optionD;
    countdown.innerHTML = "30";
    answers.style.display = "block"
    closeBtn.style.display = "none"
    document.getElementById("option-one").checked = false;
    document.getElementById("option-two").checked = false;
    document.getElementById("option-three").checked = false;
    document.getElementById("option-four").checked = false;
    countdown.style.display = "block"
        // Show the modal
    modal.showModal(); // Pop up question for the answer
    let d1 = new Date()
    startTime = d1.getTime()
    timerRun = true;
    timeDisplay = startTimer(29)
    timer = setTimeout(function() {noAnswer()}, 30000)
}

function startTimer(duration) {
    var timer = duration, seconds;
    const t = setInterval(function () {
        seconds = parseInt(timer % 60, 10);

        seconds = seconds < 10 ? "0" + seconds : seconds;

        countdown.innerHTML = seconds;

        if (--timer < 0) {
            timer = duration;
        }
        if (seconds <= 0 || timerRun == false) {
            clearInterval(t)
        }
    }, 1000);
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