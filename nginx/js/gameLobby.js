import { openMatchmakingWebsocket } from './websockets.js';
import { closeMatchmakingWebsocket } from './websockets.js';
import { textDotLoading } from './animations.js';
import { openRematchWebsocket } from "./websockets.js";
import { closeRematchWebsocket } from "./websockets.js";
import { openLocalPlayWebsocket } from "./websockets.js";
import { openPongWebsocket} from './websockets.js';
import { apiCallAuthed } from './api.js';
import { showToast } from "./notifications.js";

export function init() {
	localStorage.removeItem("match_id");

	let mode = localStorage.getItem("gameMode");
	if (mode == "ai" || mode == "tournamentLocal" || mode == "tournamentRemote")
	{
		localStorage.setItem("gameMode", "local");
		mode = "local";
	}
	const last_match_id = localStorage.getItem("prev_match_id");

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
	{
		handleMatchRedirect();
	}
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

async function handleMatchRedirect()
{
	// event.preventDefault();
	try {
		const response = await apiCallAuthed(`/api/pong/matches-ip`, "GET", null, null);
		if(response.match_id == 0)
		{
			openMatchmakingWebsocket();
			return
		}
		localStorage.setItem("match_id", response.match_id);
		openPongWebsocket(response.match_id, "join");
	} catch (error) {
		window.location.hash = '#dashboard'
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
	}
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
		// console.log("LOCAL PLAY ID ", response.match_id);
		localStorage.setItem("match_id", response.match_id);
		openLocalPlayWebsocket(response.match_id);
	} catch (error) {
		// console.error("Error creating local match:", error);
		showToast("Error creating local match", null, error, "t_matchCreateLocal");
		window.location.hash = "#dashboard";
	}
}

// Create a local match rematch
async function createLocalPlayRematch(side_mode) {
	const prev_match_id = localStorage.getItem("prev_match_id")

	try {
		const url = "/api/localplay/" + prev_match_id + "/rematch/" + side_mode 
		const response = await apiCallAuthed(url, "POST", null, null);
		// console.log("LOCAL PLAY rematch ID ", response.match_id);
		localStorage.setItem("match_id", response.match_id);
		openLocalPlayWebsocket(response.match_id);
	} catch (error) {
		// console.error("Error creating local rematch:", error);
		showToast("Error creating local rematch", null, error, "t_rematchCreateLocal");
		window.location.hash = "#dashboard";
	}
}

function showLocalPlayPage() {
	const localPlayPage = document.getElementById("localPlayPage");
    localPlayPage.style.display = 'block';
}