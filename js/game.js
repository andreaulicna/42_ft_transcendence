// props to BroCode: https://www.youtube.com/watch?v=AiFqApeurqI

export function init() {

	// CANVAS SETTINGS 
	const gameBoard = document.querySelector("#gameBoard");
	const ctx = gameBoard.getContext("2d");
	const scoreText = document.querySelector("#scoreText");
	const gameWidth = gameBoard.width;
	const gameHeight = gameBoard.height;
	const paddle1Color = "#00babc";
	const paddle2Color = "#df2af7";
	const ballColor = "whitesmoke";
	const ballRadius = 12.5;

	// DEFAULT GAME SETTINGS 
	let intervalID;
	let aiIntervalID;
	let ballSpeed;
	let ballX = gameWidth / 2;
	let ballY = gameHeight / 2;
	let ballXDirection = 0;
	let ballYDirection = 0;
	let player1Score = 0;
	let player2Score = 0;
	let paddle1 = {
		width: 25,
		height: 100,
		x: 0,
		y: 0
	};
	let paddle2 = {
		width: 25,
		height: 100,
		x: gameWidth - 25,
		y: gameHeight - 100
	};
	let keys = {};
	window.addEventListener("keydown", (event) => keys[event.keyCode] = true);
	window.addEventListener("keyup", (event) => keys[event.keyCode] = false);
	let gameMode = localStorage.getItem('gameMode');
	let aiTargetY = paddle2.y + paddle2.height / 2;

	// CUSTOMIZABLE GAME SETTINGS
	const paddleSpeed = 5;
	const aiSpeed = 5;
	const winCondition = 1;

	// GAME LOGIC
	gameStart();

	function gameStart(){
		createBall();
		nextTick();
		if (gameMode == 'ai') {
			setInterval(predictAIPaddlePosition, 1000); // Predict AI paddle position every 1 second
			aiIntervalID = setInterval(moveAIPaddle, 10); // Update AI paddle position every 10 miliseconds
		}
	}

	function nextTick(){
		intervalID = setTimeout(() => {
			clearBoard();
			drawPaddles();
			movePaddles();
			moveBall();
			drawBall(ballX, ballY);
			checkCollision();
			requestAnimationFrame(nextTick);
		}, 10)
	}

	function clearBoard(){
		ctx.clearRect(0, 0, gameWidth, gameHeight);
	}

	function drawPaddles(){
		ctx.shadowBlur = 20;
		ctx.shadowColor = paddle1Color;
		ctx.fillStyle = paddle1Color;
		ctx.fillRect(paddle1.x, paddle1.y, paddle1.width, paddle1.height);
		ctx.shadowColor = paddle2Color;
		ctx.fillStyle = paddle2Color;
		ctx.fillRect(paddle2.x, paddle2.y, paddle2.width, paddle2.height);
		// Reset shadow properties to avoid affecting other drawings
		ctx.shadowBlur = 0;
		ctx.shadowColor = 'transparent';
	}

	function createBall(){
		ballSpeed = 3;
		if(Math.round(Math.random()) == 1){
			ballXDirection =  1; 
		}
		else{
			ballXDirection = -1; 
		}
		if(Math.round(Math.random()) == 1){
			ballYDirection = Math.random() * 1;
		}
		else{
			ballYDirection = Math.random() * -1;
		}
		ballX = gameWidth / 2;
		ballY = gameHeight / 2;
		drawBall(ballX, ballY);
	}

	function moveBall(){
		ballX += (ballSpeed * ballXDirection);
		ballY += (ballSpeed * ballYDirection);
	}

	function drawBall(ballX, ballY){
		ctx.shadowBlur = 20;
		ctx.shadowColor = ballColor;
		ctx.fillStyle = ballColor;
		ctx.beginPath();
		ctx.arc(ballX, ballY, ballRadius, 0, 2 * Math.PI);
		ctx.fill();
		// Reset shadow properties to avoid affecting other drawings
		ctx.shadowBlur = 0;
		ctx.shadowColor = 'transparent';
	}

	function checkCollision(){
		if(ballY <= ballRadius){
			ballYDirection *= -1;
		}
		if(ballY >= gameHeight - ballRadius){
			ballYDirection *= -1;
		}
		if(ballX <= 0){
			player2Score += 1;
			updateScore();
			createBall();
			return;
		}
		if(ballX >= gameWidth){
			player1Score += 1;
			updateScore();
			createBall();
			return;
		}
		if(ballX <= (paddle1.x + paddle1.width + ballRadius)){
			if(ballY > paddle1.y && ballY < paddle1.y + paddle1.height){
				ballX = paddle1.x + paddle1.width + ballRadius; // if ball gets stuck
				ballXDirection *= -1;
				ballSpeed += 1;
			}
		}
		if(ballX >= (paddle2.x - ballRadius)){
			if(ballY > paddle2.y && ballY < paddle2.y + paddle2.height){
				ballX = paddle2.x - ballRadius; // if ball gets stuck
				ballXDirection *= -1;
				ballSpeed += 1;
			}
		}
	}

	function movePaddles() {
		const paddle1Up = 87;
		const paddle1Down = 83;
		const paddle2Up = 38;
		const paddle2Down = 40;

		if (keys[paddle1Up] && paddle1.y > 0) {
			paddle1.y -= paddleSpeed;
		}
		if (keys[paddle1Down] && paddle1.y < gameHeight - paddle1.height) {
			paddle1.y += paddleSpeed;
		}
		if (gameMode != "ai")
		{
			if (keys[paddle2Up] && paddle2.y > 0) {
				paddle2.y -= paddleSpeed;
			}
			if (keys[paddle2Down] && paddle2.y < gameHeight - paddle2.height) {
				paddle2.y += paddleSpeed;
			}
		}
	}

	function moveAIPaddle() {
		if (aiTargetY < paddle2.y + paddle2.height / 2 && paddle2.y > 0) {
			paddle2.y -= aiSpeed;
		}
		if (aiTargetY > paddle2.y + paddle2.height / 2 && paddle2.y < gameHeight - paddle2.height) {
			paddle2.y += aiSpeed;
		}
	}

	function predictAIPaddlePosition() {
		aiTargetY = predictBall();
	}

	function predictBall() {
		let predictedBallX = ballX;
		let predictedBallY = ballY;
		let predictedBallXDirection = ballXDirection;
		let predictedBallYDirection = ballYDirection;
		const maxSteps = 1000; // Limit the number of prediction steps to prevent infinite loop
		let steps = 0;

		while (predictedBallX < gameWidth - paddle2.width && steps < maxSteps) {
			predictedBallX += (ballSpeed * predictedBallXDirection);
			predictedBallY += (ballSpeed * predictedBallYDirection);

			// Check for collisions with the top and bottom walls
			if (predictedBallY <= ballRadius || predictedBallY >= gameHeight - ballRadius) {
				predictedBallYDirection *= -1;
			}
			steps++;
		}
		return predictedBallY;
	}
	
	function updateScore(){
		scoreText.textContent = `${player1Score} : ${player2Score}`;
		if (player1Score >= winCondition || player2Score >= winCondition)
			endGame();
	}

	function resetGame() {
		// Reset scores
		player1Score = 0;
		player2Score = 0;
		updateScore();
		
		// Reset paddle positions
		paddle1.y = 0;
		paddle2.y = gameHeight - paddle2.height;
	
		// Clear any existing intervals
		clearTimeout(intervalID);
		clearInterval(aiIntervalID);
	
		// Restart the game
		gameStart();
	}

	function endGame(){
		alert("Game over!");
		resetGame();
	}
}