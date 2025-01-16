import { openPongWebsocket } from "./websockets.js";

function reconnectToGame()
{
	if (localStorage.getItem("in_game") == "YES" && localStorage.getItem("match_id"))
		openPongWebsocket(localStorage.getItem("match_id"));
}

reconnectToGame();