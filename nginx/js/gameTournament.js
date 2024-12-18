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
	matchID,
	setMatchID,

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
import { addTournamentMatchEndListener } from "./websockets.js";

let tournamentRoundNumber = 0;
const tournamentCapacity = parseInt(sessionStorage.getItem("tournament_capacity"), 10);
const tournamentRoundMax = Math.log2(tournamentCapacity);

export async function init() {
	let data = await apiCallAuthed(`/api/user/match/${sessionStorage.getItem("match_id")}`);
	startCountdown();
	initGameData(data);
	initEventListeners();
	initTournamentEventListeners();
	initMatchData(data);
	initPaddleEventDispatch();
	drawTick();
	if (isTouchDevice) {
		await delay(100);
		initTouchControls(player1Data);
		console.log("TOUCH CONTROLS ENABLED");
	}
	// Replay for tournament disabled
	replayButton.style.display = "none";
}

async function initMatchData(data) {
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
}

function initTournamentEventListeners()
{
	addTournamentMatchEndListener();
	window.addEventListener('tournament_end', handleTournamentEnd);
	window.addEventListener('match_end', handleTournamentGameOver);
}

export function handleTournamentGameOver() {
	setMatchID(sessionStorage.getItem("match_id"));
	tournamentRoundNumber++;
	console.log("ROUND NUMBER", tournamentRoundNumber);
	console.log("MAX ROUNDS", tournamentRoundMax);
	const winnerID = player1.score > player2.score ? player1Data.id : player2Data.id;
	const loserID = player1.score > player2.score ? player2Data.id : player1Data.id;
	if (sessionStorage.getItem("id") == winnerID) {
		dispatchWinnerMatchEnd(winnerID, matchID);
		// if (tournamentRoundNumber >= tournamentRoundMax)
		// 	window.location.hash = "winner-tnmt";
		hideGameOverScreen();
	} else if (sessionStorage.getItem("id") == loserID) {
		closeTournamentWebsocket();
		window.location.hash = '#dashboard';
	}
}

function dispatchWinnerMatchEnd(winnerID, matchID) {
	const message ={
		message: "match_end",
		match_id: matchID,
		winner_id: winnerID
	};
	const event = new CustomEvent('tournamentMatchEnd', { detail: message });
	// console.log("DISPATCHING END MATCH MSG", message);
	window.dispatchEvent(event);
}

function handleTournamentEnd() {
	console.log("HANDLING TOURNAMENT END");
	const winnerID = player1.score > player2.score ? player1Data.id : player2Data.id;
	const loserID = player1.score > player2.score ? player2Data.id : player1Data.id;
	console.log(`my ID: ${sessionStorage.getItem("id")}, winner ID: ${winnerID}, loser ID: ${loserID}`);
	closeTournamentWebsocket();
	if (sessionStorage.getItem("id") == winnerID)
	{
		window.location.hash = "winner-tnmt";
	}
	else if (sessionStorage.getItem("id") == loserID)
	{
		window.location.hash = '#dashboard';
	}
}