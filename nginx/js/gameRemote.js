import {
	player1Data,
	player2Data,
	player1,
	player2,
	player1AvatarPlaceholder,
	player2AvatarPlaceholder,
	fetchPlayer1Data,
	fetchPlayer2Data,
	setPlayer1Name,
	setPlayer2Name,

	initGameData,
	initEventListeners,
	initPaddleEventDispatch,
	drawTick,
	startCountdown,

	replayButton
} from './gameCore.js';

import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";

export async function init() {
	let data = await apiCallAuthed(`/api/user/match/${localStorage.getItem("match_id")}`);
	// startCountdown();
	initGameData(data);
	initEventListeners();
	initRemoteData(data);
	initPaddleEventDispatch();
	drawTick();
}

async function initRemoteData(data) {
	await fetchPlayer1Data(data);
	await fetchPlayer2Data(data);

	setPlayer1Name(player1Data.username);
	setPlayer2Name(player2Data.username);

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
	
	if (player1Data.avatar != null)
		player1AvatarPlaceholder.src = player1Data.avatar;
	if (player2Data.avatar != null)
		player2AvatarPlaceholder.src = player2Data.avatar;

	replayButton.addEventListener("click", () => {
		localStorage.setItem("gameMode", "rematch");
		window.location.hash = '#lobby-game';
	});
}