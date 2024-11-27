import { openMatchmakingWebsocket } from './websockets.js';
import { closeMatchmakingWebsocket } from './websockets.js';

export function init() {
	// Open Matchmaking Websocket
	openMatchmakingWebsocket();

	// Function to close the Matchmaking Websocket and return to main menu
	function returnToMenu()
	{
		closeMatchmakingWebsocket();
		window.location.hash = '#dashboard';
	}

	const returnButton = document.getElementById('stopSearchingBtn');
	if (returnButton) {
		returnButton.addEventListener('click', returnToMenu);
	}

	// Simple loading animation
	const loadingAnimation = document.getElementById("loadingAnimation");
	let dots = 0;
	const animationSpeed = 400;

	const intervalId = setInterval(() => {
		dots = (dots + 1) % 4;
		loadingAnimation.textContent = '.'.repeat(dots) || '.';
	}, animationSpeed);

	// Clear the interval when the page unloads
	window.addEventListener('beforeunload', () => {
		clearInterval(intervalId);
	});
}