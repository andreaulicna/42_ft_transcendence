import { openMatchmakingWebsocket } from './websockets.js';
import { closeMatchmakingWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';

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

	textDotLoading("loadingAnimation");
}