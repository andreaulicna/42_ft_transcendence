import { apiCallAuthed } from './api.js';

export async function openWebSocket(url) {
	try {
		const response = await apiCallAuthed('/api/auth/ws-login', 'GET');
		const uuid = response.uuid;
		sessionStorage.setItem('uuid', uuid);

		const ws = new WebSocket(url + `?uuid=${uuid}`);

		ws.onopen = () => {
			console.log('WebSocket connection opened');
		};

		ws.onclose = () => {
			console.log('WebSocket connection closed');
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
		};

		ws.onmessage = (event) => {
			const data = event.data;
			console.log('WebSocket message received:', data);
			if (url == "/api/matchmaking/ws/")
			{
				openPongWebsocket(data.match_id);
			}
		};
	} catch (error) {
		console.error('Error searching for player:', error);
	}
}

export async function openFriendlistWebsocket()
{
    const url = "/api/auth/ws/init/";
    openWebSocket(url);
    console.log('Friendlist WebSocket established');
}

export async function openMatchmakingWebsocket()
{
    const url = "/api/matchmaking/ws/";
    openWebSocket(url);
    console.log('Matchmaking WebSocket established');
}

export async function openPongWebsocket(match_id)
{
    const url = "/api/pong/ws/" + match_id + "/";
    openWebSocket(url);
    console.log('Pong WebSocket established');
}