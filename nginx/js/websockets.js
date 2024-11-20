import { apiCallAuthed } from './api.js';

let pongWebSocket; // Declare a variable to store the Pong WebSocket instance

export async function openWebSocket(url) {
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
					openPongWebsocket(data.message);
				}
				// For an ongoing match, dispatch custom events based on the message type
				if (data.type === "match_start") {
					const matchStartEvent = new CustomEvent('match_start', { detail: data });
					window.dispatchEvent(matchStartEvent);
				} else if (data.type === "draw") {
					const drawEvent = new CustomEvent('draw', { detail: data });
					window.dispatchEvent(drawEvent);
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
	openWebSocket(url).then(() => {
		console.log('Friendlist WebSocket established');
	});
}

export async function openMatchmakingWebsocket() {
	const url = "/api/matchmaking/ws/";
	window.searchingPlayerModal.show(); // Open the 'Searching for player' modal
	openWebSocket(url).then(() => {
		console.log('Matchmaking WebSocket established');
	}).catch((error) => {
		console.error('Failed to establish Matchmaking WebSocket:', error);
	});
}

export async function openPongWebsocket(match_id) {
	const url = "/api/pong/ws/" + match_id + "/";
	openWebSocket(url).then((ws) => {
		pongWebSocket = ws; // Store the Pong WebSocket instance
		const modalBackdrop = document.querySelector('.modal-backdrop');
		if (modalBackdrop) {
			modalBackdrop.remove(); // Remove the backdrop element from the DOM
		}
		window.searchingPlayerModal.hide(); // Close the modal when match found
		console.log('Pong WebSocket established');
		// Add a small delay before the redirect to compensate for the slow-ass closing of the shitty-ass modal
		setTimeout(() => {
			window.location.hash = '#game'; // Redirect to #game when the connection is established
		}, 100);
	}).catch((error) => {
		console.error('Failed to establish Pong WebSocket:', error);
	});
}

// Listen for paddle movement events and send them through the Pong WebSocket
window.addEventListener('paddle_movement', (event) => {
	if (pongWebSocket && pongWebSocket.readyState === WebSocket.OPEN) {
		pongWebSocket.send(JSON.stringify(event.detail));
		console.log('PONG WebSocket message sent:', event.detail);
	}
});