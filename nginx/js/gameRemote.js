import {
    gameMode,
    gameBoard,
    ctx,
    originalGameWidth,
    originalGameHeight,
    gameWidth,
    gameHeight,
    scaleX,
    scaleY,
    keys,
    matchID,
    ball,
    paddle1,
    paddle2,
    paddle1Color,
    paddle2Color,
    ballColor,
    playerNames,
    scoreText,
    player1AvatarPlaceholder,
    player2AvatarPlaceholder,
    gameOverScreen,
    winnerName,
    replayButton,
    mainMenuButton,
    initGameData,
	drawTick,
	delay
} from './gameCore.js';

import {
	initTouchControls,
	isTouchDevice,
	touchControlsPlayer1,
	touchControlsPlayer2,
	player1Up,
	player1Down,
	player2Up,
	player2Down
} from './gameTouchControls.js';

import { apiCallAuthed } from './api.js';
import { addPaddleMovementListener, closeTournamentWebsocket } from './websockets.js';
import { addTournamentMatchEndListener } from './websockets.js';
import { textDynamicLoad } from "./animations.js";

/* 👇 DATA DECLARATION */

let tournamentRoundNumber;
let tournamentCapacity;
let tournamentRoundMax;

/* 👇 DATA INITIALIZATION */
function initGameData(data)
{

	if (gameMode == "tournament")
	{
		tournamentRoundNumber = 0;
		tournamentCapacity = parseInt(sessionStorage.getItem("tournament_capacity"), 10);
		tournamentRoundMax = Math.log2(tournamentCapacity);
	}
}

async function initPlayerData(data)
{
	// console.log("Match data", data);
	player1Data = await apiCallAuthed(`api/user/${data.player1}/info`);
	// console.log("Player 1 data", player1Data);
	player2Data = await apiCallAuthed(`api/user/${data.player2}/info`);
	// console.log("Player 2 data", player2Data);

	player1 = {
		name: player1Data.username,
		score: 0,
	}

	player2 = {
		name: player2Data.username,
		score: 0,
	}

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
	
	if (player1Data.avatar != null)
		player1AvatarPlaceholder.src = player1Data.avatar;
	if (player2Data.avatar != null)
		player2AvatarPlaceholder.src = player2Data.avatar;
}

function initEventListeners()
{
	if (gameMode == "tournament")
	{
		addTournamentMatchEndListener();
		window.addEventListener('tournament_end', handleTournamentEnd);
	}

	// Disable the replay button in tournaments
	if (gameMode == "tournament")
	{
		replayButton.style.display = "none";
	}
}

/* 👇 MENUS & REMATCH & NON-GAME LOGIC */

/* 👇 TOURNAMENT LOGIC */
function dispatchWinnerMatchEnd(winnerId, matchId) {
	const message ={
		message: "match_end",
		match_id: matchId,
		winner_id: winnerId
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

/* 👇 GAME INIT */

export async function init() {
	let data = await apiCallAuthed(`/api/user/match/${sessionStorage.getItem("match_id")}`);
	startCountdown();
	initGameData(data);
	initEventListeners();
	initPlayerData(data);
	drawTick();
	if (isTouchDevice) {
		await delay(100);
		initTouchControls(player1Data);
		console.log("TOUCH CONTROLS ENABLED");
	}
}