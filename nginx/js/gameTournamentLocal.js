import {
	player1,
	player2,
	setPlayer1Name,
	setPlayer2Name,
	matchID,
	setMatchID,

	initGameData,
	initEventListeners,
	initPaddleEventDispatch,
	drawTick,
	startCountdown,
	hideGameOverScreen,
	resetScore,

	replayButton,
	mainMenuButton,
	continueButton,
} from './gameCore.js';

import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";
import { addLocalTournamentMatchEndListener, closeLocalTournamentWebsocket } from "./websockets.js";

let data;
let winner;

export async function init() {
	data = await apiCallAuthed(`/api/user/localmatch/${localStorage.getItem("match_id")}`);
	setMatchID(localStorage.getItem("match_id"));
	startCountdown();
	initGameData(data);
	initEventListeners();
	initTournamentEventListeners();
	initLocalData(data);
	initPaddleEventDispatch();
	drawTick();

	// Only permit the 'continue' button
	replayButton.style.display = "none";
	mainMenuButton.style.display = "none";
	continueButton.style.display = "block";
}

async function initLocalData(data)
{
	setPlayer1Name(data.player1_tmp_username);
	setPlayer2Name(data.player2_tmp_username);

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
}

function initTournamentEventListeners()
{
	addLocalTournamentMatchEndListener();
	window.addEventListener('tournament_end', handleTournamentEnd);
	window.addEventListener('match_end', dispatchWinnerMatchEnd);

	continueButton.addEventListener("click", () => {
		nextGame();
	});
}

function dispatchWinnerMatchEnd() {
	winner = player1.score > player2.score ? player1.name : player2.name;
	const message ={
		message: "match_end",
		match_id: matchID,
		winner_username: winner,
	};
	const event = new CustomEvent('tournamentMatchEnd', { detail: message });
	// console.log("DISPATCHING END MATCH MSG", message);
	window.dispatchEvent(event);
}

function handleTournamentEnd() {
	console.log("HANDLING TOURNAMENT END");
	closeLocalTournamentWebsocket();
	window.location.hash = "winner-tnmt";
}

async function nextGame() {
	drawTick();
	resetScore();
	data = await apiCallAuthed(`/api/user/match/${localStorage.getItem("match_id")}`);
	initMatchData(data);
	hideGameOverScreen();
	startCountdown();
}