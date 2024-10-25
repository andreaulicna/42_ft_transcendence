let touchPaddle1 = null;
let touchPaddle2 = null;

export function initializeTouchControls(gameBoard, paddle1, paddle2, gameWidth, gameHeight) {
	gameBoard.addEventListener("touchstart", handleTouchStart, false);
	gameBoard.addEventListener("touchmove", handleTouchMove, false);
	gameBoard.addEventListener("touchend", handleTouchEnd, false);

	function handleTouchStart(event) {
		event.preventDefault();
		
		for (let i = 0; i < event.touches.length; i++) {
			const touch = event.touches[i];
			if (touch.clientX < gameWidth / 2 && touchPaddle1 === null) {
				touchPaddle1 = touch.identifier;
				console.log(`Assigned touchPaddle1: ${touch.identifier}`);
			} else if (touch.clientX >= gameWidth / 2 && touchPaddle2 === null) {
				touchPaddle2 = touch.identifier;
				console.log(`Assigned touchPaddle2: ${touch.identifier}`);
			}
		}
	}

	function handleTouchMove(event) {
		for (let i = 0; i < event.touches.length; i++) {
			const touch = event.touches[i];
			if (touch.identifier === touchPaddle1) {
				paddle1.y = touch.clientY - paddle1.height / 2;
				if (paddle1.y < 0) paddle1.y = 0;
				if (paddle1.y > gameHeight - paddle1.height) paddle1.y = gameHeight - paddle1.height;
				console.log(`Moving paddle1: ${touch.identifier}`);
			} else if (touch.identifier === touchPaddle2) {
				paddle2.y = touch.clientY - paddle2.height / 2;
				if (paddle2.y < 0) paddle2.y = 0;
				if (paddle2.y > gameHeight - paddle2.height) paddle2.y = gameHeight - paddle2.height;
				console.log(`Moving paddle2: ${touch.identifier}`);
			}
		}
	}

	function handleTouchEnd(event) {
		for (let i = 0; i < event.changedTouches.length; i++) {
			const touch = event.changedTouches[i];
			if (touch.identifier === touchPaddle1) {
				touchPaddle1 = null;
				console.log(`Released touchPaddle1: ${touch.identifier}`);
			} else if (touch.identifier === touchPaddle2) {
				touchPaddle2 = null;
				console.log(`Released touchPaddle2: ${touch.identifier}`);
			}
		}
	}
}