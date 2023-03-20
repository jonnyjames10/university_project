import Ball from './Ball.js';
import Paddle from './Paddle.js';

const ball = new Ball(document.getElementById("ball"));
const playerPaddle = new Paddle(document.getElementById("player-paddle"));
const computerPaddle = new Paddle(document.getElementById("computer-paddle"));
const playerScoreElem = document.getElementById("player-score");
const computerScoreElem = document.getElementById("computer-score");
const modal = document.querySelector('#modal');
const closeModal = document.querySelector('.close-button');

let lastTime;
let playing = true;

function update(time) {
    if (lastTime != null) {
        const delta = time - lastTime;
        // ball.update(delta, [playerPaddle.rect(), computerPaddle.rect()]);
        computerPaddle.update(delta, ball.y);
        const hue = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--hue"));

        document.documentElement.style.setProperty("--hue", hue + delta * 0.01);

        if (isLose()) {
            handleLose();
            window.requestAnimationFrame(pause);
        }
    }
    
    lastTime = time;
    window.requestAnimationFrame(update);
}

function pause(time) {
    if (playing == true) {
        window.requestAnimationFrame(update);
    }

    if (lastTime != null) {
        const delta = time - lastTime;
        computerPaddle.update(delta, ball.y);
        playerPaddle.update(delta, ball.y);
        const hue = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--hue"));

        document.documentElement.style.setProperty("--hue", hue + delta * 0.01);

    }
    
    lastTime = time;
    window.requestAnimationFrame(pause);
}

function isLose() {
    const rect = ball.rect();
    return rect.right >= window.innerWidth || rect.left <= 0;
}

closeModal.addEventListener('click', () => {
    modal.close();
    playing = true;
})

async function handleLose() {
    playing = false;
    const rect = ball.rect();
    if (rect.right >= window.innerWidth) {
        playerScoreElem.textContent = parseInt(playerScoreElem.textContent) + 1;
    } else {
        computerScoreElem.textContent = parseInt(computerScoreElem.textContent) + 1;
    }
    window.requestAnimationFrame(pause);
    modal.showModal(); // Pop up question for the answer
    ball.reset();
    computerPaddle.reset();
}

document.addEventListener("mousemove", e =>  {
    playerPaddle.position = (e.y / window.innerHeight) * 100;
})

if (playing == true) {
    window.requestAnimationFrame(update);
} else {
    window.requestAnimationFrame(pause);
}