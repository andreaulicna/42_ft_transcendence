import { paddle1Keys, paddle2Keys } from './gameCore.js';

export let touchControlsPlayer1;
export let touchControlsPlayer2;
export let player1Up;
export let player1Down;
export let player2Up;
export let player2Down;

export function initTouchControls()
{
	const gameMode = localStorage.getItem("gameMode")
	touchControlsPlayer1 = document.getElementById('touchControlsPlayer1');
	touchControlsPlayer2 = document.getElementById('touchControlsPlayer2');
	player1Up = document.getElementById('player1Up');
	player1Down = document.getElementById('player1Down');
	player2Up = document.getElementById('player2Up');
	player2Down = document.getElementById('player2Down');

	touchControlsPlayer1.style.setProperty('display', 'block', 'important');
	if (gameMode === 'local' || gameMode === "local-rematch-switch" || gameMode === "local-rematch")
		touchControlsPlayer2.style.setProperty('display', 'block', 'important');
	else
		touchControlsPlayer2.style.setProperty('display', 'none', 'important');

	function handleTouchStart(event, key, paddleKeys) {
		// console.log("touchStart");
		event.preventDefault();
		paddleKeys[key] = true;
	}

	function handleTouchEnd(event, key, paddleKeys) {
		// console.log("touchEnd");
		event.preventDefault();
		paddleKeys[key] = false;
	}

	player1Up.addEventListener('touchstart', (event) => handleTouchStart(event, 87, paddle1Keys));
	player1Up.addEventListener('touchend', (event) => handleTouchEnd(event, 87, paddle1Keys));

	player1Down.addEventListener('touchstart', (event) => handleTouchStart(event, 83, paddle1Keys));
	player1Down.addEventListener('touchend', (event) => handleTouchEnd(event, 83, paddle1Keys));

	player2Up.addEventListener('touchstart', (event) => handleTouchStart(event, 38, paddle2Keys));
	player2Up.addEventListener('touchend', (event) => handleTouchEnd(event, 38, paddle2Keys));

	player2Down.addEventListener('touchstart', (event) => handleTouchStart(event, 40, paddle2Keys));
	player2Down.addEventListener('touchend', (event) => handleTouchEnd(event, 40, paddle2Keys));
}