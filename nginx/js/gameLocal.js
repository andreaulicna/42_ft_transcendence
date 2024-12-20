import {
	player1,
	player2,
	setPlayer1Name,
	setPlayer2Name,

	initGameData,
	initEventListeners,
	initPaddleEventDispatch,
	drawTick,
	startCountdown,
	replayButton,
} from './gameCore.js';

import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";

export async function init() {
	let data = await apiCallAuthed(`/api/user/localmatch/${sessionStorage.getItem("match_id")}`);
	startCountdown();
	initGameData(data);
	initEventListeners();
	initLocalData(data);
	initPaddleEventDispatch();
	drawTick();
	// Replay for local matches disabled (needs to be reworked first)
	replayButton.style.display = "none";
}

async function initLocalData(data)
{
	setPlayer1Name(data.player1_tmp_username);
	setPlayer2Name(data.player2_tmp_username);

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
}