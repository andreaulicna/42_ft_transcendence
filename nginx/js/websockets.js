import { apiCallAuthed } from './api.js';
import { handleFriendStatusUpdate } from './profile.js';
import { handleLobbyStatusUpdate } from './tournamentLobby.js';
import { handleGracePeriod } from './gameCore.js';
import { showToast } from './notifications.js';

let pongWebSocket;
let statusWebSocket;
let matchmakingWebSocket;
let tournamentWebSocket;
let localTournamentWebSocket;
let localWebSocket;
let rematchWebSocket;
let aiplayWebSocket;

// Refactor this catch-all function so it doesn't handle multiple websocket types?
// + open the websockets from their respective files to prevent all of this unnecessarry
// event dispatching shit
async function openWebSocket(url, type) {
	return new Promise(async (resolve, reject) => {
		try {
			const response = await apiCallAuthed('/api/auth/ws-login', 'GET');
			const uuid = response.uuid;
			sessionStorage.setItem('uuid', uuid);

			const ws = new WebSocket(url + `?uuid=${uuid}`);

			ws.onopen = () => {
				console.log(`${type} WebSocket connection opened`);
				resolve(ws);
			};

			ws.onclose = () => {
				console.log(`${type} WebSocket connection closed`);
			};

			ws.onerror = (error) => {
				// console.error(`${type} WebSocket error:`, error);
				reject(error);
			};

			ws.onmessage = (event) => {
				const data = JSON.parse(event.data);
				// Show all messages except the draw type
				if (data.type != "draw")
					console.log('WebSocket message received:', data);
				// Game initialization
				if (type == "matchmaking" || type == "rematch"
					|| (type == "tournament" && data.type != "remote_tournament_lobby_update"))
				{
					if (data.message != "tournament_end")
					{
						localStorage.setItem("match_id", data.message);
						openPongWebsocket(data.message, "join");
					}
				}
				if (data.type == "local_tournament_message")
				{
					if (data.message != "tournament_end")
					{
						localStorage.setItem("match_id", data.message);
						openLocalPlayWebsocket(data.message);
					}
				}
				// Dispatch custom events based on the message type received from server
				if (data.type === "draw")
				{
					const drawEvent = new CustomEvent('draw', { detail: data });
					window.dispatchEvent(drawEvent);
				}
				else if (data.type === "match_start")
				{
					const matchStartEvent = new CustomEvent('match_start', { detail: data });
					window.dispatchEvent(matchStartEvent);
				}
				else if (data.type === "match_end")
				{
					const matchEndEvent = new CustomEvent('match_end', { detail: data });
					window.dispatchEvent(matchEndEvent);
				}
				else if (data.message === "brackets")
				{
					const bracketsEvent = new CustomEvent('brackets', { detail: data });
					window.dispatchEvent(bracketsEvent);
				}
				else if (data.message === "tournament_end")
				{
					const tournamentEndEvent = new CustomEvent('tournament_end');
					// console.log("TOURNAMENT END MESSAGE RECEIVED");
					window.dispatchEvent(tournamentEndEvent);
				}
				else if (data.type === "user_status")
				{
					handleFriendStatusUpdate(data);
				}
				else if (data.type === "remote_tournament_lobby_update")
				{
					handleLobbyStatusUpdate(data);
				}
				else if (data.type === "grace_disconnect")
				{
					handleGracePeriod();
				}
				else if (data.type === "in_game")
				{
					console.log("User disconnected from a game, attempting to reconnect.");
					localStorage.setItem("match_id", data.match_id);
					openPongWebsocket(data.match_id, "reconnect");
				}
			};
		} catch (error) {
			// console.error(`Error opening WebSocket ${type} :`, error);
			reject(error);
		}
	});
}

export async function openStatusWebsocket() {
	const url = "/api/ws/auth/init/";
	openWebSocket(url, "status").then((ws) => {
		statusWebSocket = ws;
		// console.log('Status WebSocket established');
	}).catch((error) => {
		// console.error('Failed to establish Status WebSocket:', error);
	});
}

export async function openMatchmakingWebsocket() {
	const url = "/api/ws/matchmaking/";
	openWebSocket(url, "matchmaking").then((ws) => {
		matchmakingWebSocket = ws;
		// console.log('Matchmaking WebSocket established');
	}).catch((error) => {
		// console.error('Failed to establish Matchmaking WebSocket:', error);
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
		window.location.hash = "#dashboard";
	});
}

export async function openRematchWebsocket(rematch_id) {
	const url = `api/ws/matchmaking/${rematch_id}/rematch/`;
	openWebSocket(url, "rematch").then((ws) => {
		rematchWebSocket = ws;
		// console.log('Rematch WebSocket established');
	}).catch((error) => {
		// console.error('Failed to establish Rematch WebSocket:', error);
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
		window.location.hash = '#dashboard';
	});
}

export async function openTournamentWebsocket(tournament_id) {
	const url = "/api/ws/tournament/" + tournament_id + "/";
	openWebSocket(url, "tournament").then((ws) => {
		tournamentWebSocket = ws;
		// console.log('Tournament WebSocket established');
	}).catch((error) => {
		// console.error('Failed to establish Tournament WebSocket:', error);
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
	});
}

export async function openLocalTournamentWebsocket(tournament_id) {
	const url = "/api/ws/tournament/local/" + tournament_id + "/";
	openWebSocket(url, "local_tournament").then((ws) => {
		localTournamentWebSocket = ws;
		// console.log('Local Tournament WebSocket established');
	}).catch((error) => {
		// console.error('Failed to establish Local Tournament WebSocket:', error);
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
	});
}

export async function openPongWebsocket(match_id, flag) {
	const url = "/api/ws/pong/" + match_id + "/";
	openWebSocket(url, "pong").then((ws) => {
		pongWebSocket = ws;
		// console.log('Pong WebSocket established');
		window.location.hash = '#game';
	}).catch((error) => {
		// console.error('Failed to establish Pong WebSocket:', error);
		if (flag == "reconnect")
			showToast("Error", "The match is no longer ongoing.", null, "t_matchNoLongerOngoing");
		if (flag == "join")
		{
			showToast("Error", "Cannot start game session", null, "t_openingWsError");
			window.location.hash = "#dashboard";
		}
	});
}

export async function openLocalPlayWebsocket(match_id) {
	const url = "/api/ws/localplay/" + match_id + "/";
	openWebSocket(url, "localplay").then((ws) => {
		localWebSocket = ws;
		// console.log('LocalPlay WebSocket established');
		window.location.hash = '#game';
	}).catch((error) => {
		// console.error('Failed to establish LocalPlay WebSocket:', error);
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
	});
}

export async function openAIPlayWebsocket(match_id) {
	const url = "/api/ws/ai/" + match_id + "/";
	openWebSocket(url, "aiplay").then((ws) => {
		aiplayWebSocket = ws;
		// console.log('AIPlay WebSocket established');
		window.location.hash = '#game';
	}).catch((error) => {
		// console.error('Failed to establish AIPlay WebSocket:', error);
		showToast("Error", "Cannot start game session", null, "t_openingWsError");
	});
}

function closeWebSocket(ws) {
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.close();
		console.log('WebSocket connection closed');
	}
}

export function closeStatusWebsocket() {
	closeWebSocket(statusWebSocket);
}

export function closeLocalWebsocket() {
	closeWebSocket(localWebSocket);
}

export function closeMatchmakingWebsocket() {
	closeWebSocket(matchmakingWebSocket);
}

export function closeRematchWebsocket() {
	closeWebSocket(rematchWebSocket);
}

export function closeTournamentWebsocket() {
	closeWebSocket(tournamentWebSocket);
}

export function closeLocalTournamentWebsocket() {
	closeWebSocket(localTournamentWebSocket);
}

export function closePongWebsocket() {
	closeWebSocket(pongWebSocket);
}

export function closeAIPlayWebsocket() {
	closeWebSocket(aiplayWebSocket);
}

/* ON/OFF STATUS LOGIC */

const broadcastChannel = new BroadcastChannel("ws_channel");

broadcastChannel.onmessage = (event) => {
	if (event.data == "logout")
	{
		// Close all WebSockets
		closeStatusWebsocket();
		closeLocalWebsocket();
		closeMatchmakingWebsocket();
		closeRematchWebsocket();
		closeTournamentWebsocket();
		closeLocalTournamentWebsocket()
		closePongWebsocket();
		closeAIPlayWebsocket();
		console.log('WebSockets closed due to user logout.');
	}
};

let statusRefreshEventListenerAdded = false;

export function listenStatusRefreshEvent() {
	if (!statusRefreshEventListenerAdded)
	{
		window.addEventListener('refresh_status', handleStatusRefreshEvent);
		statusRefreshEventListenerAdded = true;
	}
}

function handleStatusRefreshEvent() {
	if (statusWebSocket && statusWebSocket.readyState === WebSocket.OPEN)
		statusWebSocket.send(JSON.stringify("refresh"));
}


/* GAME LOGIC */

// Send paddle movement from game to Localplay/Pong websocket
function handlePaddleMovement(event) {
	if (pongWebSocket && pongWebSocket.readyState === WebSocket.OPEN) {
		pongWebSocket.send(JSON.stringify(event.detail));
		// console.log('PONG WebSocket message sent:', event.detail);
	}
	else if (localWebSocket && localWebSocket.readyState === WebSocket.OPEN) {
		localWebSocket.send(JSON.stringify(event.detail));
		// console.log('Localplay WebSocket message sent:', event.detail);
	}
	else if (aiplayWebSocket && aiplayWebSocket.readyState === WebSocket.OPEN) {
		aiplayWebSocket.send(JSON.stringify(event.detail));
		// console.log('AIPlay WebSocket message sent:', event.detail);
	}
}

export function addPaddleMovementListener() {
		window.addEventListener('paddle_movement', handlePaddleMovement);
}

/* TOURNAMENT LOGIC */
	
// Let server know when a tournament match ends
function handleTournamentMatchEnd(event) {
	// console.log("INTERCEPTED MATCH END MSG");
	if (tournamentWebSocket) {
		// console.log("Tournament WebSocket exists, readyState:", tournamentWebSocket.readyState);
	} else {
		// console.log("Tournament WebSocket is not initialized");
	}
	if (tournamentWebSocket && tournamentWebSocket.readyState === WebSocket.OPEN)
	{
		tournamentWebSocket.send(JSON.stringify(event.detail));
		console.log('Tournament WebSocket message sent:', event.detail);
	}
}

export function addTournamentMatchEndListener() {
	// console.log("ADDING MATCH END LISTENER");
	window.addEventListener('tournamentMatchEnd', handleTournamentMatchEnd);
}

/* LOCAL TOURNAMENT LOGIC */
	
function handleLocalTournamentMatchEnd(event) {
	if (localTournamentWebSocket && localTournamentWebSocket.readyState === WebSocket.OPEN)
	{
		localTournamentWebSocket.send(JSON.stringify(event.detail));
		console.log('Local Tournament WebSocket message sent:', event.detail);
	}
}

export function addLocalTournamentMatchEndListener() {
	// console.log("ADDING TOURNAMENT MATCH END LISTENER");
	window.addEventListener('localTournamentMatchEnd', handleLocalTournamentMatchEnd);
}

function handleLocalTournamentContinue(event) {
	if (localTournamentWebSocket && localTournamentWebSocket.readyState === WebSocket.OPEN)
	{
		localTournamentWebSocket.send(JSON.stringify(event.detail));
		console.log('Local Tournament WebSocket message sent:', event.detail);
	}
}

export function addLocalTournamentContinueListener() {
	window.addEventListener('localTournamentContinue', handleLocalTournamentContinue);
}

