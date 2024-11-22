import { apiCallAuthed } from './api.js';
import { initializeTouchControls } from './gameTouchControls.js';

export async function init(data) {
	window.addEventListener('draw', handleDraw);
	window.addEventListener('match_end', showGameOverScreen);

	startCountdown();

	/* 👇 DEFAULT GAME OBJECTS INITIALIZATON */

	console.log("Match data", data);
	const originalGameWidth = 160; // Server-side game width
	const originalGameHeight = 100; // Server-side game height

	const player1Data = await apiCallAuthed(`api/user/${data.player1}/info`);
	console.log("Player 1 data", player1Data);
	const player2Data = await apiCallAuthed(`api/user/${data.player2}/info`);
	console.log("Player 2 data", player2Data);

	let player1 = {
		name: player1Data.username,
		score: 0,
	}

	let player2 = {
		name: player2Data.username,
		score: 0,
	}

	let ball = {
		x: originalGameWidth / 2,
		y: originalGameHeight / 2,
		radius: data.default_ball_size,
	}

	let paddle1 = {
		width: data.default_paddle_width,
		height: data.default_paddle_height,
		x: 80,
		y: 0,
	};

	let paddle2 = {
		width: data.default_paddle_width,
		height: data.default_paddle_height,
		x: -80,
		y: 0,
	};

	// CANVAS SETTINGS 
	const gameBoard = document.getElementById("gameBoard");
	const ctx = gameBoard.getContext("2d");
	const playerNames = document.getElementById("playerNames");
	const player1NamePlaceholder = document.getElementById("player1Name");
	const player2NamePlaceholder = document.getElementById("player2Name");
	player1NamePlaceholder.textContent = player1.name;
	player2NamePlaceholder.textContent = player2.name;

	// Uncomment this after the avatar upload is in place

	// const player1AvatarPlaceholder = document.getElementById("player1Pic");
	// const player2AvatarPlaceholder = document.getElementById("player2Pic");
	// player1AvatarPlaceholder.src = player1Data.avatar;
	// player2AvatarPlaceholder.src = player2Data.avatar;

	const scoreText = document.getElementById("scoreText");
	const gameWidth = gameBoard.width;
	const gameHeight = gameBoard.height;
	const paddle1Color = "#00babc";
	const paddle2Color = "#df2af7";
	const ballColor = "whitesmoke";

	// Calculate the drawing scale for client's viewport
	const scaleX = gameWidth / originalGameWidth;
	const scaleY = gameHeight / originalGameHeight;

	/* 👇 GAME LOGIC */

	// PLAYER CONTROLS
	let keys = {};
	window.addEventListener("keydown", (event) => keys[event.keyCode] = true);
	window.addEventListener("keyup", (event) => keys[event.keyCode] = false);
	initializeTouchControls(gameBoard, paddle1, paddle2, gameWidth, gameHeight);

	// LISTEN TO DRAW EVENT AND DRAW THE FRAME

	function handleDraw(event) {
		const data = event.detail;
		ball.x = (data.ball_x + originalGameWidth / 2) * scaleX;
		ball.y = (data.ball_y + originalGameHeight / 2) * scaleY;
		paddle1.x = (data.paddle1_x + originalGameWidth / 2) * scaleX;
		paddle1.y = (data.paddle1_y + originalGameHeight / 2) * scaleY;
		paddle2.x = (data.paddle2_x + originalGameWidth / 2) * scaleX;
		paddle2.y = (data.paddle2_y + originalGameHeight / 2) * scaleY;
		player1.score = data.player1_score;
		player2.score = data.player2_score;

		clearBoard();
		drawPaddles(paddle1, paddle2);
		drawBall(ball);
		updateScore();
		sendPaddleMovement();
	}

	// CLEAR BOARD
	function clearBoard() {
		ctx.clearRect(0, 0, gameWidth, gameHeight);
	}

	// DRAW PADDLES
	function drawPaddles(paddle1, paddle2) {
		ctx.shadowBlur = 20;
		ctx.shadowColor = paddle1Color;
		ctx.fillStyle = paddle1Color;
		ctx.fillRect(paddle1.x - (paddle1.width / 2), paddle1.y - (paddle2.height / 2), paddle1.width * scaleX, paddle1.height * scaleY);
		ctx.shadowColor = paddle2Color;
		ctx.fillStyle = paddle2Color;
		ctx.fillRect(paddle2.x - (paddle2.width / 2), paddle2.y - (paddle2.height / 2), paddle2.width * scaleX, paddle2.height * scaleY);
		ctx.shadowBlur = 0;
		ctx.shadowColor = 'transparent';
	}

	// DRAW BALL
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

	// PADDLE MOVEMENT
	function sendPaddleMovement() {
		let direction = null;
		if (keys[87] && paddle1.y > 0) {
			direction = "UP";
		} else if (keys[83] && paddle1.y < gameHeight - paddle1.height * scaleY) {
			direction = "DOWN";
		}
	
		if (direction) {
			const paddleMovementEvent = new CustomEvent('paddle_movement', {
				detail: {
					type: "paddle_movement",
					direction: direction
				}
			});
			window.dispatchEvent(paddleMovementEvent);
		}
	}

	/* 👇 MENUS & NON-GAME LOGIC */

	// START COUNTDOWN
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

	// GAME OVER SCREEN ELEMENTS
	const gameOverScreen = document.getElementById("gameOverScreen");
	const winnerName = document.getElementById("winnerName");
	const replayButton = document.getElementById("replayButton");
	const mainMenuButton = document.getElementById("mainMenuButton");

	// UPDATE SCORE
	function updateScore() {
		scoreText.textContent = `${player1.score} : ${player2.score}`;
	}

	// SHOW GAME OVER SCREEN
	function showGameOverScreen() {
		let winner = player1.score > player2.score ? player1.name : player2.name;
		winnerName.textContent = `${winner}`;
		winnerName.className = player1.score > player2.score ? "blueSide" : "redSide";

		gameOverScreen.style.display = "block";
		gameBoard.style.display = "none";
		playerNames.style.visibility = "hidden";
		scoreText.style.display = "none";
	}

	// HIDE GAME OVER SCREEN
	function hideGameOverScreen() {
		gameOverScreen.style.display = "none";
		gameBoard.style.display = "block";
		playerNames.style.visibility = "visible";
		scoreText.style.display = "block";
	}

	replayButton.addEventListener("click", () => {
		hideGameOverScreen();
		// resetGame();
	});

	mainMenuButton.addEventListener("click", () => {
		hideGameOverScreen();
	});

	// // RESET GAME
	// function resetGame() {
	// 	player1Score = 0;
	// 	player2Score = 0;
	// 	ballX = gameWidth / 2;
	// 	ballY = gameHeight / 2;
	// 	ballXDirection = 0;
	// 	ballYDirection = 0;
	// 	paddle1.y = 0;
	// 	paddle2.y = gameHeight - paddle2.height * scaleY;
	// 	updateScore();
	// 	gameStart();
	// }
}