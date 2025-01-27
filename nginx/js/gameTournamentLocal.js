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
	delay,

	replayButton,
	mainMenuButton,
	continueButton,
	initMatchStartListener,
} from './gameCore.js';

import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";

import { addLocalTournamentContinueListener,
	addLocalTournamentMatchEndListener,
	closeLocalTournamentWebsocket,
} from "./websockets.js";

let data;
let winner;

export async function init() {
	initMatchStartListener();
	data = await apiCallAuthed(`/api/user/localmatch/${localStorage.getItem("match_id")}`);
	setMatchID(localStorage.getItem("match_id"));
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
	addLocalTournamentContinueListener();
	window.addEventListener("match_end", dispatchWinnerMatchEnd);
	window.addEventListener('tournament_end', handleTournamentEnd);
	window.addEventListener("match_start", nextGame);
	window.addEventListener("brackets", (event) => renderTournamentBracket(event))
	continueButton.addEventListener("click", dispatchContinue);
}

function dispatchWinnerMatchEnd() {
	winner = player1.score > player2.score ? player1.name : player2.name;
	const message ={
		message: "match_end",
		match_id: matchID,
		winner_username: winner,
	};
	const event = new CustomEvent('localTournamentMatchEnd', { detail: message });
	window.dispatchEvent(event);
}

function dispatchContinue()
{
	const message ={
		message: "continue"
	};
	const event = new CustomEvent('localTournamentContinue', { detail: message });
	window.dispatchEvent(event);
}

function handleTournamentEnd() {
	window.removeEventListener("brackets", renderTournamentBracket);
	localStorage.removeItem('tournament_id');
	closeLocalTournamentWebsocket();
	window.location.hash = "winner-tnmt";
}

async function nextGame() {
	drawTick();
	resetScore();
	await delay(100);
	setMatchID(localStorage.getItem("match_id"));
	data = await apiCallAuthed(`/api/user/localmatch/${matchID}`);
	initLocalData(data);
	initPaddleEventDispatch();
	hideGameOverScreen();
}

function renderTournamentBracket(event) {
	const data = event.detail;

	const players = data.brackets;
	const capacity = data.capacity;
	const bracketContainer = document.getElementById("bracket-container");
	bracketContainer.innerHTML = "";
	bracketContainer.classList.add("d-flex", "justify-content-center", "align-items-center", "bracket-style");

	const totalRounds = Math.log2(capacity);
	let matchIndex = 0; // Initialize match index

	for (let round = 1; round <= totalRounds; round++) {
		const roundContainer = document.createElement("div");
		roundContainer.className = "round-container";

		const heading = document.createElement("h5");
		const roundText = document.createElement("span");
		roundText.setAttribute("data-translate", "round");
		roundText.innerText = "Round";
		heading.appendChild(roundText);
		heading.appendChild(document.createTextNode(` ${round}`));
		roundContainer.appendChild(heading);

		// Number of matches in this round = capacity / 2^round
		const matchesThisRound = capacity / Math.pow(2, round);

		for (let match = 0; match < matchesThisRound; match++) {
			const matchContainer = document.createElement("div");
			matchContainer.className = "match-container";

			let p1 = players[matchIndex].player1_username ? players[matchIndex].player1_username : "❓";
			let p2 = players[matchIndex].player2_username ? players[matchIndex].player2_username : "❓";

			matchContainer.innerHTML = `
			<div class="player-slot">${p1}</div>
			<span>⚔️</span>
			<div class="player-slot">${p2}</div>
			`;

			roundContainer.appendChild(matchContainer);
			matchIndex++; // Increment match index
		}
		bracketContainer.appendChild(roundContainer);
	}
}