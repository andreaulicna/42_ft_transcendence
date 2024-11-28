import { apiCallAuthed } from './api.js';
import { addPaddleMovementListener } from './websockets.js';

/* 👇 DATA DECLARATION */
let gameMode;
let gameBoard;
let ctx;
let originalGameWidth; // Server-side game width
let originalGameHeight; // Server-side game height
let gameWidth;
let gameHeight;
let scaleX; // Calculate the drawing scale for client's viewport
let scaleY;
let keys;

let player1Data;
let player2Data;
let player1 = {};
let player2 = {};

let ball = {};
let paddle1 = {};
let paddle2 = {};
let paddle1Color;
let paddle2Color;
let ballColor;

let playerNames;
let scoreText;
let player1NamePlaceholder;
let player2NamePlaceholder;
let player1AvatarPlaceholder;
let player2AvatarPlaceholder;
let gameOverScreen;
let winnerName;
let replayButton;
let mainMenuButton;

let isTouchDevice;

/* 👇 DATA INITIALIZATION */
function initGameData(data)
{
	gameMode = localStorage.getItem('gameMode');
	gameBoard = document.getElementById("gameBoard");
	ctx = gameBoard.getContext("2d");
	originalGameWidth = 160;
	originalGameHeight = 100;
	gameWidth = gameBoard.width;
	gameHeight = gameBoard.height;
	scaleX = gameWidth / originalGameWidth;
	scaleY = gameHeight / originalGameHeight;
	keys = {};

	ball = {
		x: (originalGameWidth / 2) * scaleX,
		y: (originalGameHeight / 2) * scaleX,
		radius: data.default_ball_size / 2,
	}

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

	isTouchDevice = 'ontouchstart' in window;
}

async function initPlayerData(data)
{
	console.log("Match data", data);
	player1Data = await apiCallAuthed(`api/user/${data.player1}/info`);
	console.log("Player 1 data", player1Data);
	player2Data = await apiCallAuthed(`api/user/${data.player2}/info`);
	console.log("Player 2 data", player2Data);

	player1 = {
		name: player1Data.username,
		score: 0,
	}

	player2 = {
		name: player2Data.username,
		score: 0,
	}

	player1NamePlaceholder.textContent = player1.name;
	player2NamePlaceholder.textContent = player2.name;
	
	if (player1Data.avatar != null)
		player1AvatarPlaceholder.src = player1Data.avatar;
	if (player2Data.avatar != null)
		player2AvatarPlaceholder.src = player2Data.avatar;
}

function initEventListeners()
{
	if (!window.keyListenersAdded) {
		window.addEventListener("keydown", handleKeyDown);
		window.addEventListener("keyup", handleKeyUp);
		window.keyListenersAdded = true;
	}

	window.addEventListener('draw', handleDraw);
	window.addEventListener('match_end', showGameOverScreen);

	replayButton.addEventListener("click", () => {
		hideGameOverScreen();
	});
	
	mainMenuButton.addEventListener("click", () => {
		hideGameOverScreen();
	});

	addPaddleMovementListener();
}

function initGameBoardVisual()
{
	// Draw the objects once before the game starts to visually initialize them
	clearBoard();
	drawPaddles(paddle1, paddle2);
	drawBall(ball);
}

function initTouchControls(player1Data)
{		
	const touchControlsPlayer1 = document.getElementById('touchControlsPlayer1');
	const touchControlsPlayer2 = document.getElementById('touchControlsPlayer2');
	const player1Up = document.getElementById('player1Up');
	const player1Down = document.getElementById('player1Down');
	const player2Up = document.getElementById('player2Up');
	const player2Down = document.getElementById('player2Down');

	if (gameMode === 'local') {
		touchControlsPlayer1.style.display = 'block';
		touchControlsPlayer2.style.display = 'block';
	}
	else
	{
		if (player1Data.id == sessionStorage.getItem("id"))
		{
			touchControlsPlayer1.style.display = 'block';
			touchControlsPlayer2.style.display = 'none';
		}
		else
		{
			touchControlsPlayer1.style.display = 'none';
			touchControlsPlayer2.style.display = 'block';
		}
	}

	function handleTouchStart(event, key) {
		// console.log("touchStart");
		event.preventDefault();
		keys[key] = true;
	}

	function handleTouchEnd(event, key,) {
		// console.log("touchEnd");
		event.preventDefault();
		keys[key] = false;
	}

	player1Up.addEventListener('touchstart', (event) => handleTouchStart(event, 87));
	player1Up.addEventListener('touchend', (event) => handleTouchEnd(event, 87));

	player1Down.addEventListener('touchstart', (event) => handleTouchStart(event, 83));
	player1Down.addEventListener('touchend', (event) => handleTouchEnd(event, 83));

	player2Up.addEventListener('touchstart', (event) => handleTouchStart(event, 87));
	player2Up.addEventListener('touchend', (event) => handleTouchEnd(event, 87));

	player2Down.addEventListener('touchstart', (event) => handleTouchStart(event, 83));
	player2Down.addEventListener('touchend', (event) => handleTouchEnd(event, 83));
}

/* 👇 GAME LOGIC */

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

	clearBoard();
	drawPaddles(paddle1, paddle2);
	drawBall(ball);
	updateScore();
	sendPaddleMovement();
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

function sendPaddleMovement() {
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

/* 👇 MENUS & NON-GAME LOGIC */

function startCountdown() {
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

function updateScore() {
	scoreText.textContent = `${player1.score} : ${player2.score}`;
}

function showGameOverScreen() {
	let winner = player1.score > player2.score ? player1.name : player2.name;
	winnerName.textContent = `${winner}`;
	winnerName.className = player1.score > player2.score ? "blueSide" : "redSide";

	gameOverScreen.style.display = "block";
	gameBoard.style.display = "none";
	playerNames.style.visibility = "hidden";
	scoreText.style.display = "none";
	if (isTouchDevice)
	{
		touchControlsPlayer1.style.display = 'none';
		touchControlsPlayer2.style.display = 'none';
	}		
}

function hideGameOverScreen() {
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

/* 👇 GAME INIT */

// Function to create a delay
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export async function init(data) {
	startCountdown();
	initGameData(data);
	initEventListeners();
	initPlayerData(data);
	initGameBoardVisual();
	if (isTouchDevice) {
		await delay(100);
		initTouchControls(player1Data);
		console.log("TOUCH CONTROLS ENABLED");
	}
}