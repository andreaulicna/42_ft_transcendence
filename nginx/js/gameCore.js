import { apiCallAuthed } from './api.js';
import { addPaddleMovementListener, closeTournamentWebsocket } from './websockets.js';
import { addTournamentMatchEndListener } from './websockets.js';
import { textDynamicLoad } from "./animations.js";
import { handleTournamentGameOver } from './gameTournament.js';

/* 👇 DATA DECLARATION */
export let gameMode;
export let gameBoard;
export let ctx;
export let originalGameWidth = 160; // Server-side game width
export let originalGameHeight = 100; // Server-side game height
export let gameWidth;
export let gameHeight;
export let scaleX; // Calculate the drawing scale for client's viewport
export let scaleY;
export let keys = {};

export let matchID;
export let player1Data;
export let player2Data;
export let player1 = {};
export let player2 = {};

export let ball = {};
export let paddle1 = {};
export let paddle2 = {};
export let paddle1Color;
export let paddle2Color;
export let ballColor;

export let playerNames;
export let scoreText;
export let player1AvatarPlaceholder;
export let player2AvatarPlaceholder;
export let gameOverScreen;
export let winnerName;
export let replayButton;
export let mainMenuButton;

let listenersAdded = false;

/* 👇 DATA INITIALIZATION */
export function initGameData(data) {
	matchID = data.id;
	gameMode = localStorage.getItem('gameMode');
	gameBoard = document.getElementById("gameBoard");
	ctx = gameBoard.getContext("2d");
	gameWidth = gameBoard.width;
	gameHeight = gameBoard.height;
	scaleX = gameWidth / originalGameWidth;
	scaleY = gameHeight / originalGameHeight;
	keys = {};

	ball = {
		x: (originalGameWidth / 2) * scaleX,
		y: (originalGameHeight / 2) * scaleX,
		radius: data.default_ball_size / 2,
	};

	paddle1 = {
		width: data.default_paddle_width,
		height: data.default_paddle_height,
		x: (-80 + originalGameWidth / 2) * scaleX,
		y: (0 - (data.default_paddle_height / 2) + originalGameHeight / 2) * scaleY,
	};

	paddle2 = {
		width: data.default_paddle_width,
		height: data.default_paddle_height,
		x: ((80 - data.default_paddle_width) + originalGameWidth / 2) * scaleX,
		y: (0 - (data.default_paddle_height / 2) + originalGameHeight / 2) * scaleY,
	};

	paddle1Color = "#00babc";
	paddle2Color = "#df2af7";
	ballColor = "whitesmoke";

	playerNames = document.getElementById("playerNames");
	scoreText = document.getElementById("scoreText");
	player1NamePlaceholder = document.getElementById("player1Name");
	player2NamePlaceholder = document.getElementById("player2Name");
	player1AvatarPlaceholder = document.getElementById("player1Pic");
	player2AvatarPlaceholder = document.getElementById("player2Pic");
	gameOverScreen = document.getElementById("gameOverScreen");
	winnerName = document.getElementById("winnerName");
	replayButton = document.getElementById("replayButton");
	mainMenuButton = document.getElementById("mainMenuButton");

}

export function initEventListeners() {

	if (!listenersAdded) {
		window.addEventListener("keydown", handleKeyDown);
		window.addEventListener("keyup", handleKeyUp);
		window.addEventListener('draw', handleDraw);
		window.addEventListener('match_end', showGameOverScreen);
		mainMenuButton.addEventListener("click", () => {
			window.location.hash = '#dashboard';
		});
		replayButton.addEventListener("click", () => {
			replayGame();
		});
		addPaddleMovementListener();

		listenersAdded = true;
	}
}

/* 👇 CORE GAME LOGIC */
function handleKeyDown(event) {
	keys[event.keyCode] = true;
}

function handleKeyUp(event) {
	keys[event.keyCode] = false;
}

function handleDraw(event) {
	const data = event.detail;
	ball.x = (data.ball_x + originalGameWidth / 2) * scaleX;
	ball.y = (data.ball_y + originalGameHeight / 2) * scaleY;
	paddle1.x = (data.paddle1_x - (paddle1.width / 2) + originalGameWidth / 2) * scaleX;
	paddle1.y = (data.paddle1_y - (paddle1.height / 2) + originalGameHeight / 2) * scaleY;
	paddle2.x = (data.paddle2_x - (paddle2.width / 2) + originalGameWidth / 2) * scaleX;
	paddle2.y = (data.paddle2_y - (paddle2.height / 2) + originalGameHeight / 2) * scaleY;
	player1.score = data.player1_score;
	player2.score = data.player2_score;

	drawTick();
	if (gameMode == "remote")
		remotePaddleMovement();
}

function clearBoard() {
	ctx.clearRect(0, 0, gameWidth, gameHeight);
}

function drawPaddles(paddle1, paddle2) {
	ctx.shadowBlur = 20;
	ctx.shadowColor = paddle1Color;
	ctx.fillStyle = paddle1Color;
	ctx.fillRect(paddle1.x, paddle1.y, paddle1.width * scaleX, paddle1.height * scaleY);
	ctx.shadowColor = paddle2Color;
	ctx.fillStyle = paddle2Color;
	ctx.fillRect(paddle2.x, paddle2.y, paddle2.width * scaleX, paddle2.height * scaleY);
	ctx.shadowBlur = 0;
	ctx.shadowColor = 'transparent';
}

function drawBall(ball) {
	ctx.shadowBlur = 20;
	ctx.shadowColor = ballColor;
	ctx.fillStyle = ballColor;
	ctx.beginPath();
	ctx.arc(ball.x, ball.y, ball.radius * Math.min(scaleX, scaleY), 0, 2 * Math.PI);
	ctx.fill();
	ctx.shadowBlur = 0;
	ctx.shadowColor = 'transparent';
}

function updateScore() {
	scoreText.textContent = `${player1.score} : ${player2.score}`;
}

export function drawTick()
{
	clearBoard();
	drawPaddles(paddle1, paddle2);
	drawBall(ball);
	updateScore();
}

/* 👇 REMOTE PLAY SEND MOVEMENT */

function throttle(func, limit) {
	let lastFunc;
	let lastRan;
	return function(...args) {
		const context = this;
		if (!lastRan) {
			func.apply(context, args);
			lastRan = Date.now();
		} else {
			clearTimeout(lastFunc);
			lastFunc = setTimeout(function() {
				if ((Date.now() - lastRan) >= limit) {
					func.apply(context, args);
					lastRan = Date.now();
				}
			}, limit - (Date.now() - lastRan));
		}
	};
}

const throttledDispatchEvent = throttle((direction) => {
	const paddleMovementEvent = new CustomEvent('paddle_movement', {
		detail: {
			type: "paddle_movement",
			direction: direction
		}
	});
	window.dispatchEvent(paddleMovementEvent);
}, 10);

function remotePaddleMovement() {
	let direction = null;
	if (player1Data.id == sessionStorage.getItem("id"))
	{
		if (keys[87] && paddle1.y >= 0) {
			direction = "UP";
		} else if (keys[83] && paddle1.y <= (gameHeight - paddle1.height) * scaleY) {
			direction = "DOWN";
		}
	}
	else
	{
		if (keys[87] && paddle2.y >= 0) {
			direction = "UP";
		} else if (keys[83] && paddle2.y <= (gameHeight - paddle2.height) * scaleY) {
			direction = "DOWN";
		}
	}
	
	if (direction) {
		throttledDispatchEvent(direction);
	}
}

/* 👇 MENUS & REMATCH & NON-GAME LOGIC */

export function startCountdown() {
	const countdownModal = new bootstrap.Modal(document.getElementById('countdownModal'));
	const countdownText = document.getElementById('countdownText');
	let countdown = 3;

	countdownModal.show();

	const countdownInterval = setInterval(() => {
		countdownText.textContent = countdown;
		countdown--;
		if (countdown < 0) {
			clearInterval(countdownInterval);
			countdownModal.hide();
		}
	}, 800);
}

export function showGameOverScreen() {
	let winner = player1.score > player2.score ? player1.name : player2.name;
	winnerName.textContent = `${winner}`;
	winnerName.className = player1.score > player2.score ? "blueSide" : "redSide";

	gameOverScreen.style.display = "block";
	gameBoard.style.display = "none";
	playerNames.style.visibility = "hidden";
	scoreText.style.display = "none";
	if (isTouchDevice) {
		touchControlsPlayer1.style.display = 'none';
		touchControlsPlayer2.style.display = 'none';
	}

	if (gameMode == "tournament") {
		handleTournamentGameOver();
	}
}

export function hideGameOverScreen() {
	gameOverScreen.style.display = "none";
	gameBoard.style.display = "block";
	playerNames.style.visibility = "visible";
	scoreText.style.display = "block";
	if (isTouchDevice)
	{
		touchControlsPlayer1.style.display = "block";
		touchControlsPlayer2.style.display = "block";
	}
}

async function replayGame() {
	// hideGameOverScreen();
	localStorage.setItem("gameMode", "rematch");
	window.location.hash = '#lobby-game';
}

// Function to create a delay
export function delay(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}