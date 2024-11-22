import { apiCallAuthed } from './api.js';

let pongWebSocket;
let friendlistWebSocket;
let matchmakingWebSocket;

async function openWebSocket(url) {
	return new Promise(async (resolve, reject) => {
		try {
			const response = await apiCallAuthed('/api/auth/ws-login', 'GET');
			const uuid = response.uuid;
			sessionStorage.setItem('uuid', uuid);

			const ws = new WebSocket(url + `?uuid=${uuid}`);

			ws.onopen = () => {
				console.log('WebSocket connection opened');
				resolve(ws); // Resolve the promise when the connection is opened
			};

			ws.onclose = () => {
				console.log('WebSocket connection closed');
			};

			ws.onerror = (error) => {
				console.error('WebSocket error:', error);
				reject(error); // Reject the promise if there's an error
			};

			ws.onmessage = (event) => {
				const data = JSON.parse(event.data);
				console.log('WebSocket message received:', data);
				// If match found, open Pong WebSocket
				if (url === "/api/matchmaking/ws/") {
					sessionStorage.setItem("match_id", data.message);
					openPongWebsocket(data.message);
				}
				// For an ongoing match, dispatch custom events based on the message type
				if (data.type === "draw") {
					const drawEvent = new CustomEvent('draw', { detail: data });
					window.dispatchEvent(drawEvent);
				} else if (data.type === "match_end") {
					const matchEndEvent = new CustomEvent('match_end');
					window.dispatchEvent(matchEndEvent);
				}
			};
		} catch (error) {
			console.error('Error opening WebSocket:', error);
			reject(error);
		}
	});
}

export async function openFriendlistWebsocket() {
	const url = "/api/auth/ws/init/";
	openWebSocket(url).then((ws) => {
		friendlistWebSocket = ws;
		console.log('Friendlist WebSocket established');
	});
}

export async function openMatchmakingWebsocket() {
	const url = "/api/matchmaking/ws/";
	openWebSocket(url).then((ws) => {
		matchmakingWebSocket = ws;
		console.log('Matchmaking WebSocket established');
	}).catch((error) => {
		console.error('Failed to establish Matchmaking WebSocket:', error);
	});
}

export async function openPongWebsocket(match_id) {
	const url = "/api/pong/ws/" + match_id + "/";
	openWebSocket(url).then((ws) => {
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
		console.log('WebSocket connection closed manually');
	}
}

export function closeMatchmakingWebsocket() {
	closeWebSocket(matchmakingWebSocket);
	console.log('Closing Matchmaking Websocket');
}

// Listen for paddle movement events and send them through the Pong WebSocket
window.addEventListener('paddle_movement', (event) => {
	if (pongWebSocket && pongWebSocket.readyState === WebSocket.OPEN) {
		pongWebSocket.send(JSON.stringify(event.detail));
		console.log('PONG WebSocket message sent:', event.detail);
	}
});