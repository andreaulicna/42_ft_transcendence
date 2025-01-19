import { delay } from "./gameCore.js";
import { openPongWebsocket } from "./websockets.js";

async function reconnectToGame()
{
	if (localStorage.getItem("in_game") == "YES" && localStorage.getItem("match_id"))
	{
		console.log("Status 'in_game' is set to YES, attempting to reconnect if still valid.");
		// Wait for the refresh token before attempting to open a websocket
		await delay(100);
		openPongWebsocket(localStorage.getItem("match_id"));
	}
}

reconnectToGame();