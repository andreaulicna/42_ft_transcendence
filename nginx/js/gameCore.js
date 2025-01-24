import { apiCallAuthed } from "./api.js";
import { addPaddleMovementListener } from "./websockets.js";
import {
	initTouchControls,
	touchControlsPlayer1,
	touchControlsPlayer2,
} from "./gameTouchControls.js";

/* 👇 DATA DECLARATION */
let gameMode;
let gameBoard;
let ctx;
let originalGameWidth = 160; // Server-side game width
let originalGameHeight = 100; // Server-side game height
let gameWidth;
let gameHeight;
let scaleX; // Calculate the drawing scale for client"s viewport
let scaleY;
export let matchID;
export let paddle1Keys = {};
export let paddle2Keys = {};
let lastRan = {};

let ball = {};
let paddle1 = {};
let paddle2 = {};
let paddle1Color;
let paddle2Color;
let ballColor;
let ballExactColor;
let ballPredictionColor;
let paddleAnimationFrame;

let playerNames;
let scoreText;
let gameOverScreen;
let winnerName;
export let replayButton;
export let replayButtonSwitch;
export let mainMenuButton;
export let continueButton;

export let player1Data;
export let player2Data;
export let player1 = {};
export let player2 = {};
export let player1AvatarPlaceholder;
export let player2AvatarPlaceholder;
export let isTouchDevice;

// let listenersAdded = false;

/* 👇 DATA INITIALIZATION */
export function initGameData(data) {
	matchID = data.id;
	gameMode = localStorage.getItem("gameMode");
	gameBoard = document.getElementById("gameBoard");
	ctx = gameBoard.getContext("2d");
	gameWidth = gameBoard.width;
	gameHeight = gameBoard.height;
	scaleX = gameWidth / originalGameWidth;
	scaleY = gameHeight / originalGameHeight;

	paddle1Keys = {
		87: false, // W key
		83: false, // S key
	};
	paddle2Keys = {
		38: false, // Up arrow key
		40: false, // Down arrow key
	};
	
	ball = {
		x: (originalGameWidth / 2) * scaleX,
		y: (originalGameHeight / 2) * scaleX,
		xExact: 0,
		yExact: 0,
		xPrediction: 0,
		yPrediction: 0,
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

	paddle1Color = localStorage.getItem(`${localStorage.getItem("id")}_colorLeftPaddle`) || "#00babc";
	paddle2Color = localStorage.getItem(`${localStorage.getItem("id")}_colorRightPaddle`) || "#df2af7";
	ballColor = localStorage.getItem(`${localStorage.getItem("id")}_colorBall`) || "whitesmoke";
	ballExactColor = "green";
	ballPredictionColor = "red";

	player1 = {
		name: undefined,
		score: 0,
	}

	player2 = {
		name: undefined,
		score: 0,
	}

	playerNames = document.getElementById("playerNames");
	scoreText = document.getElementById("scoreText");
	player1AvatarPlaceholder = document.getElementById("player1Pic");
	player2AvatarPlaceholder = document.getElementById("player2Pic");
	gameOverScreen = document.getElementById("gameOverScreen");
	winnerName = document.getElementById("winnerName");
	replayButton = document.getElementById("replayButton");
	replayButtonSwitch = document.getElementById("replayButtonSwitch");
	mainMenuButton = document.getElementById("mainMenuButton");
	continueButton = document.getElementById("continueButton");

	replayButton.style.display = "block";
	replayButtonSwitch.style.display = "none";
	mainMenuButton.style.display = "block";
	continueButton.style.display = "none";

	isTouchDevice = "ontouchstart" in window;
	if (isTouchDevice) {
		initTouchControls();
		console.log("TOUCH CONTROLS ENABLED");
	}
}

export function initEventListeners() {
	window.addEventListener("match_start", (event) => clearGracePeriod(event));
	window.addEventListener("keydown", handleKeyDown);
	window.addEventListener("keydown", preventArrowKeyScroll);
	window.addEventListener("keyup", handleKeyUp);
	window.addEventListener("draw", handleDraw);
	window.addEventListener("match_end", (event) => showGameOverScreen(event));
	window.addEventListener("match_end", stopPaddleEventDispatch);
	mainMenuButton.addEventListener("click", () => {
		window.location.hash = "#dashboard";
	});
	addPaddleMovementListener();
}

export function initMatchStartListener() {
	window.addEventListener("match_start", (event) => startCountdown(event));
}

function removeEventListeners() {
	window.removeEventListener("keydown", handleKeyDown);
	window.removeEventListener("keyup", handleKeyUp);
	window.removeEventListener("draw", handleDraw);
	window.removeEventListener("match_end", showGameOverScreen);
}

export async function fetchPlayer1Data(data)
{
	player1Data = await apiCallAuthed(`api/user/${data.player1}/info`);
}

export async function fetchPlayer2Data(data)
{
	player2Data = await apiCallAuthed(`api/user/${data.player2}/info`);
}

export async function fetchCreatorData(data)
{
	player1Data = await apiCallAuthed(`api/user/${data.creator}/info`);
}

export function setPlayer1Name(player1Name)
{
	player1.name = player1Name;
}

export function setPlayer2Name(player2Name)
{
	player2.name = player2Name;
}

export function setMatchID(newMatchID)
{
	matchID = newMatchID;
}

/* 👇 CORE GAME LOGIC */
function handleKeyDown(event) {
	if (paddle1Keys.hasOwnProperty(event.keyCode)) {
		paddle1Keys[event.keyCode] = true;
	}
	if (paddle2Keys.hasOwnProperty(event.keyCode)) {
		paddle2Keys[event.keyCode] = true;
	}
}

function handleKeyUp(event) {
	if (paddle1Keys.hasOwnProperty(event.keyCode)) {
		paddle1Keys[event.keyCode] = false;
	}
	if (paddle2Keys.hasOwnProperty(event.keyCode)) {
		paddle2Keys[event.keyCode] = false;
	}
}

function handleDraw(event) {
	const data = event.detail;
	ball.x = (data.ball_x + originalGameWidth / 2) * scaleX;
	ball.y = (data.ball_y + originalGameHeight / 2) * scaleY;
	if (data.ball_prediction_x == 0 && data.ball_prediction_y == 0) {
		ball.xExact = 0;
		ball.yExact = 0;
		ball.xPrediction = 0;
		ball.yPrediction = 0;
	} else {
		ball.xExact = (data.ball_exact_prediction_x + originalGameWidth / 2) * scaleX;
		ball.yExact = (data.ball_exact_prediction_y + originalGameHeight / 2) * scaleY;
		ball.xPrediction = (data.ball_prediction_x + originalGameWidth / 2) * scaleX;
		ball.yPrediction = (data.ball_prediction_y + originalGameHeight / 2) * scaleY;
	}
	paddle1.x = (data.paddle1_x - (paddle1.width / 2) + originalGameWidth / 2) * scaleX;
	paddle1.y = (data.paddle1_y - (paddle1.height / 2) + originalGameHeight / 2) * scaleY;
	paddle2.x = (data.paddle2_x - (paddle2.width / 2) + originalGameWidth / 2) * scaleX;
	paddle2.y = (data.paddle2_y - (paddle2.height / 2) + originalGameHeight / 2) * scaleY;
	player1.score = data.player1_score;
	player2.score = data.player2_score;

	drawTick();
	updateScore();
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
	ctx.shadowColor = "transparent";
}

function drawBall(ball) {
	ctx.shadowBlur = 20;
	ctx.shadowColor = ballColor;
	ctx.fillStyle = ballColor;
	ctx.beginPath();
	ctx.arc(ball.x, ball.y, ball.radius * Math.min(scaleX, scaleY), 0, 2 * Math.PI);
	ctx.fill();
	ctx.shadowBlur = 0;
	ctx.shadowColor = "transparent";
}

function drawBallExactPrediction(ball) {
	// Ball exact hit
	ctx.fillStyle = ballExactColor;
	ctx.beginPath();
	ctx.arc(ball.xExact, ball.yExact, ball.radius * Math.min(scaleX, scaleY), 0, 2 * Math.PI);
	ctx.fill();
	ctx.shadowBlur = 0;
	ctx.shadowColor = "transparent";

	// Ball predicted hit
	ctx.fillStyle = ballPredictionColor;
	ctx.beginPath();
	ctx.arc(ball.xPrediction, ball.yPrediction, ball.radius * Math.min(scaleX, scaleY), 0, 2 * Math.PI);
	ctx.fill();
	ctx.shadowBlur = 0;
	ctx.shadowColor = "transparent";
}

export function resetScore() {
	scoreText.textContent = `0 : 0`;
}

function updateScore() {
	if (player1.score == undefined || player2.score == undefined)
		scoreText.textContent = `0 : 0`;
	else
		scoreText.textContent = `${player1.score} : ${player2.score}`;
}

export function drawTick()
{
	clearBoard();
	drawPaddles(paddle1, paddle2);
	drawBall(ball);
	if (ball.xPrediction != 0 && ball.yPrediction != 0){
		drawBallExactPrediction(ball)
	}
}

/* 👇 PLAYER MOVEMENT */

function throttledDispatchEventPerKey(key, direction, paddle, limit) {
	const now = Date.now();
	if (!lastRan[key] || now - lastRan[key] >= limit) {
		const paddleMovementEvent = new CustomEvent("paddle_movement", {
			detail: {
				type: "paddle_movement",
				direction: direction,
				paddle: paddle,
			},
		});
		window.dispatchEvent(paddleMovementEvent);
		// console.log(`DISPATCHING ${paddle} MOVEMENT EVENT`);
		lastRan[key] = now;
	}
}

function sendPaddleMovement() {
	const throttleLimit = 10;

	for (const key in paddle1Keys) {
		if (paddle1Keys[key]) {
			// console.log("PLAYER 1 KEY PRESSED");
			const direction = key == 87 ? "UP" : "DOWN";
			throttledDispatchEventPerKey(key, direction, "paddle1", throttleLimit);
		}
	}

	if (gameMode == "local" || gameMode == "local-rematch" || gameMode == "local-rematch-switch" || gameMode == "tournamentLocal")
	{
		for (const key in paddle2Keys) {
			if (paddle2Keys[key]) {
				// console.log("PLAYER 2 KEY PRESSED");
				const direction = key == 38 ? "UP" : "DOWN";
				throttledDispatchEventPerKey(key, direction, "paddle2", throttleLimit);
			}
		}
	}
}

export function initPaddleEventDispatch() {
	function sendPaddleMovementFrame() {
		sendPaddleMovement();
		paddleAnimationFrame = requestAnimationFrame(sendPaddleMovementFrame);
	}

	paddleAnimationFrame = requestAnimationFrame(sendPaddleMovementFrame);
}

function stopPaddleEventDispatch() {
	if (paddleAnimationFrame) {
		cancelAnimationFrame(paddleAnimationFrame);
	}
}

/* 👇 MENUS & REMATCH & NON-GAME LOGIC */

export function startCountdown(event) {
	const data = event.detail;

	// In case of grace period reconnect, update the game state accordingly
	if (data.ball_x != 0 && data.ball_y != 0)
		handleDraw(event);

	const gameStartTime = new Date(data.game_start);
	const currentTime = new Date();
	let countdownStart = Math.floor((gameStartTime - currentTime) / 1000);

	const countdownModal = new bootstrap.Modal(document.getElementById("countdownModal"));
	const countdownNums = document.getElementById("countdownNums");

	countdownModal.show();
	countdownNums.textContent = countdownStart;

	const countdownInterval = setInterval(() => {
		countdownStart--;
		if (countdownStart > 0)
			countdownNums.textContent = countdownStart;
		else
		{
			clearInterval(countdownInterval);
			countdownModal.hide();
		}
	}, 1000);
}

function showGameOverScreen(event) {
	const data = event.detail;

	let winner = data.winner_username;
	winnerName.textContent = `${winner}`;
	winnerName.className = player1.score > player2.score ? "blueSide" : "redSide";

	gameOverScreen.style.display = "block";
	gameBoard.style.display = "none";
	playerNames.style.visibility = "hidden";
	scoreText.style.display = "none";
	if (isTouchDevice) {
		touchControlsPlayer1.style.setProperty("display", "none", "important");
		touchControlsPlayer2.style.setProperty("display", "none", "important");
	}

	// removeEventListeners();
	window.removeEventListener("keydown", preventArrowKeyScroll);
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

// Function to create a delay
export async function delay(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

// Prevent arrow key scrolling
function preventArrowKeyScroll(event) {
	const arrowKeys = ["ArrowUp", "ArrowDown"];
	if (arrowKeys.includes(event.key))
		event.preventDefault();
}

// Handle grace period for the remaining connected player
let gracePeriodInterval;
let gracePeriodModal;
let gracePeriodCountdown;

export function handleGracePeriod() {
	gracePeriodModal = new bootstrap.Modal(document.getElementById("countdownModal"));
	const countdownNums = document.getElementById("countdownNums");
	const countdownText = document.getElementById("countdownText");
	gracePeriodCountdown = 30;
	countdownText.textContent = `😒 Waiting for opponent to reconnect...`;
	countdownNums.textContent = `${gracePeriodCountdown}`;
	gracePeriodModal.show();

	gracePeriodInterval = setInterval(() => {
		gracePeriodCountdown--;
		if (gracePeriodCountdown > 0)
			countdownNums.textContent = `${gracePeriodCountdown}`;
		else
		{
			clearInterval(gracePeriodInterval);
			gracePeriodModal.hide();
		}
	}, 1000);
}

function clearGracePeriod(event) {
	if (gracePeriodInterval)
	{
		clearInterval(gracePeriodInterval);

		const data = event.detail;
		const gameStartTime = new Date(data.game_start);
		const currentTime = new Date();
		let countdownStart = Math.floor((gameStartTime - currentTime) / 1000);
		
		const countdownNums = document.getElementById("countdownNums");
		const countdownText = document.getElementById("countdownText");

		countdownNums.textContent = `${countdownStart}`;
		countdownText.textContent = ``;

		const countdownInterval = setInterval(() => {
			countdownStart--;
			countdownNums.textContent = `${countdownStart}`;
			if (countdownStart > 0)
				countdownNums.textContent = countdownStart;
			else
			{
				clearInterval(countdownInterval);
				gracePeriodModal.hide();
			}
		}, 1000);
	}
}