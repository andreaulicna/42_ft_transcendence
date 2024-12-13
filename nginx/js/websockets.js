import { apiCallAuthed } from './api.js';

let pongWebSocket;
let friendlistWebSocket;
let matchmakingWebSocket;
let tournamentWebSocket;
let rematchWebSocket;

async function openWebSocket(url, type) {
	return new Promise(async (resolve, reject) => {
		try {
			const response = await apiCallAuthed('/api/auth/ws-login', 'GET');
			const uuid = response.uuid;
			sessionStorage.setItem('uuid', uuid);

			const ws = new WebSocket(url + `?uuid=${uuid}`);

			ws.onopen = () => {
				console.log(`${type} WebSocket connection opened`);
				resolve(ws); // Resolve the promise when the connection is opened
			};

			ws.onclose = () => {
				console.log(`${type} WebSocket connection closed`);
			};

			ws.onerror = (error) => {
				console.error(`${type} WebSocket error:`, error);
				reject(error); // Reject the promise if there's an error
			};

			ws.onmessage = (event) => {
				const data = JSON.parse(event.data);
				// Show all messages except the draw type
				if (data.type != "draw")
					console.log('WebSocket message received:', data);
				if (type == "matchmaking" || type == "rematch" || type == "tournament")
				{
					sessionStorage.setItem("match_id", data.message);
					openPongWebsocket(data.message);
				}
				// For an ongoing match, dispatch custom events based on the message type received from server
				if (data.type === "draw")
				{
					const drawEvent = new CustomEvent('draw', { detail: data });
					window.dispatchEvent(drawEvent);
				}
				else if (data.type === "match_end")
				{
					const matchEndEvent = new CustomEvent('match_end');
					window.dispatchEvent(matchEndEvent);
				}
				else if (data.type === "tournament_message")
				{
					const tournamentEndEvent = new CustomEvent('tournament_end');
					window.dispatchEvent(tournamentEndEvent);
					window.tournamentEnded = true;
				}
			};
		} catch (error) {
			console.error(`Error opening WebSocket ${type} :`, error);
			reject(error);
		}
	});
}

export async function openFriendlistWebsocket() {
	const url = "/api/auth/ws/init/";
	openWebSocket(url, "friend").then((ws) => {
		friendlistWebSocket = ws;
		console.log('Friendlist WebSocket established');
	});
}

export async function openMatchmakingWebsocket() {
	const url = "/api/matchmaking/ws/";
	openWebSocket(url, "matchmaking").then((ws) => {
		matchmakingWebSocket = ws;
		console.log('Matchmaking WebSocket established');
	}).catch((error) => {
		console.error('Failed to establish Matchmaking WebSocket:', error);
	});
}

export async function openRematchWebsocket(rematch_id) {
	const url = `api/matchmaking/ws/${rematch_id}/rematch/`;
	openWebSocket(url, "rematch").then((ws) => {
		rematchWebSocket = ws;
		console.log('Rematch WebSocket established');
	}).catch((error) => {
		console.error('Failed to establish Rematch WebSocket:', error);
	});
}

export async function openTournamentWebsocket(tournament_id) {
	const url = "/api/tournament/ws/" + tournament_id + "/";
	openWebSocket(url, "tournament").then((ws) => {
		tournamentWebSocket = ws;
		console.log('Tournament WebSocket established');
	}).catch((error) => {
		console.error('Failed to establish Tournament WebSocket:', error);
	});
}

export async function openPongWebsocket(match_id) {
	const url = "/api/pong/ws/" + match_id + "/";
	openWebSocket(url, "pong").then((ws) => {
		pongWebSocket = ws;
		console.log('Pong WebSocket established');
		window.location.hash = '#game';
	}).catch((error) => {
		console.error('Failed to establish Pong WebSocket:', error);
	});
}

function closeWebSocket(ws) {
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.close();
		// console.log('WebSocket connection closed manually');
	}
}

export function closeMatchmakingWebsocket() {
	closeWebSocket(matchmakingWebSocket);
	console.log('Closing Matchmaking Websocket');
}

export function closeRematchWebsocket() {
	closeWebSocket(rematchWebSocket);
	console.log('Closing Rematch Websocket');
}

export function closeTournamentWebsocket() {
	closeWebSocket(tournamentWebSocket);
	console.log('Closing Tournament Websocket');
}

// Send paddle movement from game to Pong websocket
function handlePaddleMovement(event) {
	if (pongWebSocket && pongWebSocket.readyState === WebSocket.OPEN) {
		pongWebSocket.send(JSON.stringify(event.detail));
		// console.log('PONG WebSocket message sent:', event.detail);
	}
}

export function addPaddleMovementListener() {
		window.addEventListener('paddle_movement', handlePaddleMovement);
}

/* TOURNAMENT LOGIC */

// Let server know when a tournament match ends
function handleTournamentMatchEnd(event) {
	console.log("INTERCEPTED MATCH END MSG");
	if (tournamentWebSocket) {
		console.log("Tournament WebSocket exists, readyState:", tournamentWebSocket.readyState);
	} else {
		console.log("Tournament WebSocket is not initialized");
	}
	if (tournamentWebSocket && tournamentWebSocket.readyState === WebSocket.OPEN)
	{
		tournamentWebSocket.send(JSON.stringify(event.detail));
		console.log('Tournament WebSocket message sent:', event.detail);
	}
}

export function addTournamentMatchEndListener() {
	console.log("ADDING MATCH END LISTENER");
	window.addEventListener('tournamentMatchEnd', handleTournamentMatchEnd);
}
