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
	replayButtonSwitch,
	initMatchStartListener,
} from './gameCore.js';

import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";

export async function init() {
	initMatchStartListener();
	let data = await apiCallAuthed(`/api/user/localmatch/${localStorage.getItem("match_id")}`);
	initGameData(data);
	initEventListeners();
	initLocalData(data);
	initPaddleEventDispatch();
	drawTick();
	replayButtonSwitch.style.display = "block";

	replayButton.addEventListener("click", () => {
		localStorage.setItem("gameMode", "local-rematch");
		window.location.hash = '#lobby-game';
	});

	replayButtonSwitch.addEventListener("click", () => {
		localStorage.setItem("gameMode", "local-rematch-switch");
		window.location.hash = '#lobby-game';
	});
}


async function initLocalData(data)
{
	setPlayer1Name(data.player1_tmp_username);
	setPlayer2Name(data.player2_tmp_username);

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
}