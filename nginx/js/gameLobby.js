import { openMatchmakingWebsocket } from './websockets.js';
import { closeMatchmakingWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { openRematchWebsocket } from "./websockets.js";
import { closeRematchWebsocket } from "./websockets.js";

export function init() {
	const mode = localStorage.getItem('gameMode');
	const last_match_id = sessionStorage.getItem("match_id");

	// Change loading text if mode is rematch
	const loadingTextElement = document.getElementById('loadingText');
	if (mode == "rematch")
	{
		if (loadingTextElement)
		{
			loadingTextElement.innerHTML = `
				<span>👻</span>
				<span data-translate="waitingForRematch">Waiting for rematch</span>
			`;
		}
	}
	

	// Open corresponding Websocket
	if (mode == "remote")
		openMatchmakingWebsocket();
	else if (mode == "rematch")
		openRematchWebsocket(last_match_id);

	// Function to close the relevant Websocket and return to main menu
	function returnToMenu()
	{
		// Close corresponding Websocket
		if (mode == "remote")
			closeMatchmakingWebsocket();
		else if (mode == "rematch")
			closeRematchWebsocket(last_match_id);
		window.location.hash = '#dashboard';
	}

	const returnButton = document.getElementById('stopSearchingBtn');
	if (returnButton) {
		returnButton.addEventListener('click', returnToMenu);
	}

	textDotLoading("loadingAnimation");
}