import { openWebSocket } from './api.js';

export async function openFriendlistWebsocket()
{
    const url = "/api/auth/ws/init/";
    openWebSocket(url);
    console.log('Friendlist WebSocket established');
}