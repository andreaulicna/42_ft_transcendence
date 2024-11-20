import { initializeTouchControls } from './gameTouchControls.js';

export function init() {
	// CANVAS SETTINGS 
	const gameBoard = document.getElementById("gameBoard");
	const ctx = gameBoard.getContext("2d");
	const playerNames = document.getElementById("playerNames");
	const scoreText = document.getElementById("scoreText");
	const gameWidth = gameBoard.width;
	const gameHeight = gameBoard.height;
	const paddle1Color = "#00babc";
	const paddle2Color = "#df2af7";
	const ballColor = "whitesmoke";
	const ballRadius = 1;

	// GAME OVER SCREEN ELEMENTS
	const gameOverScreen = document.getElementById("gameOverScreen");
	const winnerName = document.getElementById("winnerName");
	const replayButton = document.getElementById("replayButton");
	const mainMenuButton = document.getElementById("mainMenuButton");

	// DEFAULT GAME SETTINGS 
	// const winCondition = 10;
	const originalGameWidth = 160; // Server-side game width
	const originalGameHeight = 100; // Server-side game height
	let ballX;
	let ballY;
	let paddle1 = {
		width: 1,
		height: 5,
		x: 80,
		y: 0,
	};
	let paddle2 = {
		width: 1,
		height: 5,
		x: -80,
		y: 0,
	};
	let gamePaused = false;
	let player1Name;
	let player2Name;
	let player1Score;
	let player2Score;

	// Calculate scaling factors
	const scaleX = gameWidth / originalGameWidth;
	const scaleY = gameHeight / originalGameHeight;

	// PLAYER CONTROLS
	let keys = {};
	window.addEventListener("keydown", (event) => keys[event.keyCode] = true);
	window.addEventListener("keyup", (event) => keys[event.keyCode] = false);
	initializeTouchControls(gameBoard, paddle1, paddle2, gameWidth, gameHeight);

	// LISTEN FOR CUSTOM EVENTS
	window.addEventListener('match_start', (event) => {
		const data = event.detail;
		player1Name = data.player1;
		player2Name = data.player2;
		gameStart();
	});

	window.addEventListener('draw', (event) => {
		const data = event.detail;
		ballX = (data.ball_x + originalGameWidth / 2) * scaleX;
		ballY = (data.ball_y + originalGameHeight / 2) * scaleY;
		paddle1.x = (data.paddle1_x + originalGameWidth / 2) * scaleX;
		paddle1.y = (data.paddle1_y + originalGameHeight / 2) * scaleY;
		paddle2.x = (data.paddle2_x + originalGameWidth / 2) * scaleX;
		paddle2.y = (data.paddle2_y + originalGameHeight / 2) * scaleY;
		player1Score = data.player1_score;
		player2Score = data.player2_score;
		// drawGame();
	});

	// // START COUNTDOWN
	// function startCountdown() {
	// 	let countdown = 3;
	// 	const countdownInterval = setInterval(() => {
	// 		scoreText.textContent = countdown;
	// 		countdown--;
	// 		if (countdown < 0) {
	// 			clearInterval(countdownInterval);
	// 			gameStart();
	// 		}
	// 	}, 1000);
	// }

	// GAME START
	function gameStart() {
		gamePaused = false;
		nextTick();
	}

	// NEXT TICK
	function nextTick() {
		if (gamePaused) return;

		setTimeout(() => {
			clearBoard();
			drawPaddles();
			drawBall(ballX, ballY);
			updateScore();
			sendPaddleMovement();
			requestAnimationFrame(nextTick);
		}, 10);
	}

	// CLEAR BOARD
	function clearBoard() {
		ctx.clearRect(0, 0, gameWidth, gameHeight);
	}

	// DRAW PADDLES
	function drawPaddles() {
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

	// DRAW BALL
	function drawBall(ballX, ballY) {
		ctx.shadowBlur = 20;
		ctx.shadowColor = ballColor;
		ctx.fillStyle = ballColor;
		ctx.beginPath();
		ctx.arc(ballX, ballY, ballRadius * Math.min(scaleX, scaleY), 0, 2 * Math.PI);
		ctx.fill();
		ctx.shadowBlur = 0;
		ctx.shadowColor = 'transparent';
	}

	// PADDLE MOVEMENT
	function sendPaddleMovement() {
		let direction = null;
		if (keys[87]) { // W key
			direction = "UP";
		} else if (keys[83]) { // S key
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

	// UPDATE SCORE
	function updateScore() {
		scoreText.textContent = `${player1Score} : ${player2Score}`;
		// if (player1Score >= winCondition || player2Score >= winCondition) {
		// 	showGameOverScreen();
		// }
	}

	// // SHOW GAME OVER SCREEN
	// function showGameOverScreen() {
	// 	let winner = player1Score >= winCondition ? player1Name : player2Name;
	// 	winnerName.textContent = `${winner}`;
	// 	winnerName.className = player1Score >= winCondition ? "blueSide" : "redSide";

	// 	gameOverScreen.style.display = "block";
	// 	gameBoard.style.display = "none";
	// 	playerNames.style.visibility = "hidden";
	// 	scoreText.style.display = "none";

	// 	gamePaused = true;
	// }

	// // HIDE GAME OVER SCREEN
	// function hideGameOverScreen() {
	// 	gameOverScreen.style.display = "none";
	// 	gameBoard.style.display = "block";
	// 	playerNames.style.visibility = "visible";
	// 	scoreText.style.display = "block";
	// }

	// replayButton.addEventListener("click", () => {
	// 	hideGameOverScreen();
	// 	// resetGame();
	// });

	// mainMenuButton.addEventListener("click", () => {
	// 	// hideGameOverScreen();
	// });

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