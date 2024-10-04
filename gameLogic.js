// props to BroCode: https://www.youtube.com/watch?v=AiFqApeurqI

export function initializeGame() {
    const gameBoard = document.querySelector("#gameBoard");
	const ctx = gameBoard.getContext("2d");
	const scoreText = document.querySelector("#scoreText");
	const gameWidth = gameBoard.width;
	const gameHeight = gameBoard.height;
	const paddle1Color = "#00babc";
	const paddle2Color = "#df2af7";
	const ballColor = "whitesmoke";
	const ballRadius = 12.5;
	const paddleSpeed = 50;
	let intervalID;
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
	window.addEventListener("keydown", changeDirection);
	gameStart();
	function gameStart(){
	    createBall();
	    nextTick();
	}
	function nextTick(){
	    intervalID = setTimeout(() => {
	        clearBoard();
	        drawPaddles();
	        moveBall();
	        drawBall(ballX, ballY);
	        checkCollision();
	        nextTick();
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
	    ballSpeed = 1;
	    if(Math.round(Math.random()) == 1){
	        ballXDirection =  1; 
	    }
	    else{
	        ballXDirection = -1; 
	    }
	    if(Math.round(Math.random()) == 1){
	        ballYDirection = Math.random() * 1; // more random directions
	    }
	    else{
	        ballYDirection = Math.random() * -1; // more random directions
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
	function changeDirection(event){
	    const keyPressed = event.keyCode;
	    const paddle1Up = 87;
	    const paddle1Down = 83;
	    const paddle2Up = 38;
	    const paddle2Down = 40;
	    switch(keyPressed){
	        case paddle1Up:
	            if(paddle1.y > 0){
	                paddle1.y -= paddleSpeed;
	            }
	            break;
	        case paddle1Down:
	            if(paddle1.y < gameHeight - paddle1.height){
	                paddle1.y += paddleSpeed;
	            }
	            break;
	        case paddle2Up:
	            if(paddle2.y > 0){
	                paddle2.y -= paddleSpeed;
	            }
	            break;
	        case paddle2Down:
	            if(paddle2.y < gameHeight - paddle2.height){
	                paddle2.y += paddleSpeed;
	            }
	            break;
	    }
	}
	function updateScore(){
	    scoreText.textContent = `${player1Score} : ${player2Score}`;
	}
}