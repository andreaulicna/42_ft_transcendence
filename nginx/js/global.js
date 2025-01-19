import { openPongWebsocket } from "./websockets.js";

function reconnectToGame()
{
	if (localStorage.getItem("in_game") == "YES" && localStorage.getItem("match_id"))
	{
		console.log("Status 'in_game' is set to YES, attempting to reconnect if still valid.");
		openPongWebsocket(localStorage.getItem("match_id"));
	}
}

reconnectToGame();