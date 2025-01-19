import { openMatchmakingWebsocket } from './websockets.js';
import { closeMatchmakingWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { openRematchWebsocket } from "./websockets.js";
import { closeRematchWebsocket } from "./websockets.js";
import { openLocalPlayWebsocket } from "./websockets.js";
import { apiCallAuthed } from './api.js';
import { showToast } from "./notifications.js";

export function init() {
	const mode = localStorage.getItem('gameMode');
	const last_match_id = localStorage.getItem("match_id");

	// Change loading text in different modes
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
	else if (mode == "local")
	{
		if (loadingTextElement)
		{
			loadingTextElement.innerHTML = `
				<span>👻</span>
				<span data-translate="localPlayCreate">Create local match</span>
			`;
		}
	}
	if (mode == "local")
	{
		showLocalPlayPage();
		const LocalPlayCreateForm = document.getElementById("create-localplay-form");
		LocalPlayCreateForm.addEventListener("submit", (e) => createLocalPlay(e));
	}
	else if (mode == "local-rematch-switch")
	{
		createLocalPlayRematch("switch");
	}
	else if (mode == "local-rematch")
	{
		createLocalPlayRematch("keep");
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
		localStorage.setItem("match_id", response.match_id);
		openLocalPlayWebsocket(response.match_id);
	} catch (error) {
		console.error("Error creating local match:", error);
		showToast("Error", error);
	}
}

// Create a local match rematch
async function createLocalPlayRematch(side_mode) {
	const prev_match_id = localStorage.getItem("match_id")

	try {
		const url = "/api/localplay/" + prev_match_id + "/rematch/" + side_mode 
		const response = await apiCallAuthed(url, "POST", null, null);
		console.log("LOCAL PLAY rematch ID ", response.match_id);
		localStorage.setItem("match_id", response.match_id);
		openLocalPlayWebsocket(response.match_id);
	} catch (error) {
		console.error("Error creating local rematch:", error);
		showToast("Error", error);
	}
}

function showLocalPlayPage() {
	const localPlayPage = document.getElementById("localPlayPage");
    localPlayPage.style.display = 'block';
}