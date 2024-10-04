// props to BroCode: https://www.youtube.com/watch?v=AiFqApeurqI

function initializeGame() {
    const gameBoard = document.querySelector("#gameBoard");
    if (!gameBoard) {
        console.error("Game board element not found!");
        return;
    }
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
}