import { openMatchmakingWebsocket } from './websockets.js';
import { closeMatchmakingWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { openRematchWebsocket } from "./websockets.js";
import { closeRematchWebsocket } from "./websockets.js";
import { openLocalPlayWebsocket } from "./websockets.js";
import { apiCallAuthed } from './api.js';


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
	if (mode == "local")
	{
		showLocalPlayPage();
		const LocalPlayCreateForm = document.getElementById("create-localplay-form");
		LocalPlayCreateForm.addEventListener("submit", (e) => createLocalPlay(e));
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

// Create a local match
async function createLocalPlay(event) {
	event.preventDefault();

	const player1TmpUsername = document.getElementById("local-player1-tmp-username").value;
	const player2TmpUsername = document.getElementById("local-player2-tmp-username").value;

	try {
		const payload = {
			'player1_tmp_username': player1TmpUsername,
			'player2_tmp_username': player2TmpUsername,
		};

		const response = await apiCallAuthed(`/api/localplay/match`, "POST", null, payload);
		console.log("LOCAL PLAY ID ", response.match_id);
		sessionStorage.setItem("match_id", response.match_id);
		openLocalPlayWebsocket(response.match_id);
	} catch (error) {
		console.error("Error creating local match:", error);
		alert("An error occurred while creating a local match.");
	}
}

function showLocalPlayPage() {
	const localPlayPage = document.getElementById("localPlayPage");
    localPlayPage.style.display = 'block';
}