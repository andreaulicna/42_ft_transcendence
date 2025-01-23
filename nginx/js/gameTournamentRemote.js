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
	startCountdown,
	hideGameOverScreen,
	resetScore,

	replayButton,
	mainMenuButton,
	initMatchStartListener,
} from './gameCore.js';

import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";
import { addTournamentMatchEndListener, closeTournamentWebsocket } from "./websockets.js";

let tournamentRoundNumber = 0;
const tournamentCapacity = parseInt(localStorage.getItem("tournament_capacity"), 10);
const tournamentRoundMax = Math.log2(tournamentCapacity);

export async function init() {
	initMatchStartListener();
	let data = await apiCallAuthed(`/api/user/match/${localStorage.getItem("match_id")}`);
	initGameData(data);
	initEventListeners();
	initTournamentEventListeners();
	initMatchData(data);
	initPaddleEventDispatch();
	drawTick();
	// Game over buttons are disabled in tournament mode
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
	window.addEventListener('match_start', resetGame);
}

export function handleTournamentGameOver() {
	setMatchID(localStorage.getItem("match_id"));
	tournamentRoundNumber++;
	console.log("ROUND NUMBER", tournamentRoundNumber);
	console.log("MAX ROUNDS", tournamentRoundMax);
	const winnerID = player1.score > player2.score ? player1Data.id : player2Data.id;
	const loserID = player1.score > player2.score ? player2Data.id : player1Data.id;
	if (localStorage.getItem("id") == winnerID) {
		dispatchWinnerMatchEnd(winnerID, matchID);
		mainMenuButton.style.display = "none";
		// if (tournamentRoundNumber >= tournamentRoundMax)
		// 	window.location.hash = "winner-tnmt";
	} else if (localStorage.getItem("id") == loserID) {
		closeTournamentWebsocket();
		// window.location.hash = '#dashboard';
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
	console.log(`my ID: ${localStorage.getItem("id")}, winner ID: ${winnerID}, loser ID: ${loserID}`);
	closeTournamentWebsocket();
	if (localStorage.getItem("id") == winnerID)
	{
		window.location.hash = "winner-tnmt";
		mainMenuButton.style.display = "block";
	}
	// else if (localStorage.getItem("id") == loserID)
	// {
	// 	window.location.hash = '#dashboard';
	// }
}

async function resetGame() {
	drawTick();
	resetScore();
	let data = await apiCallAuthed(`/api/user/match/${localStorage.getItem("match_id")}`);
	initMatchData(data);
	hideGameOverScreen();
	mainMenuButton.style.display = "block";
	initPaddleEventDispatch();
	startCountdown();
}