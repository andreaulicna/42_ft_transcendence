import {
	player1Data,
	player1,
	player2,
	player1AvatarPlaceholder,
	player2AvatarPlaceholder,
	fetchPlayer1Data,
	setPlayer1Name,
	setPlayer2Name,

	initGameData,
	initEventListeners,
	initPaddleEventDispatch,
	drawTick,
	delay,
	startCountdown,

	isTouchDevice,
} from './gameCore.js';

import { initTouchControls } from './gameTouchControls.js';
import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";

export async function init() {

	// Change URL to AI mode below
	// let data = await apiCallAuthed(`/api/user/localmatch/${sessionStorage.getItem("match_id")}`);

	startCountdown();
	initGameData(data);
	initEventListeners();
	initAIData(data);
	initPaddleEventDispatch();
	drawTick();
	if (isTouchDevice) {
		await delay(100);
		initTouchControls(player1Data);
		console.log("TOUCH CONTROLS ENABLED");
	}
	// Replay disabled (needs to be reworked first)
	replayButton.style.display = "none";
}

async function initAIData(data) {
	await fetchPlayer1Data(data);

	setPlayer1Name(player1Data.username);
	// Set a custom user name for the AI
	setPlayer2Name("Pongothon-9000");

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
	
	if (player1Data.avatar != null)
		player1AvatarPlaceholder.src = player1Data.avatar;

	// Set a custom user image for the AI
	// player2AvatarPlaceholder.src = player2Data.avatar;
}