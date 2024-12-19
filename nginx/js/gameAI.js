import {
	player1Data,
	player1,
	player2,
	player1AvatarPlaceholder,
	player2AvatarPlaceholder,
	fetchCreatorData,
	setPlayer1Name,
	setPlayer2Name,

	initGameData,
	initEventListeners,
	initPaddleEventDispatch,
	drawTick,
	delay,
	startCountdown,

	isTouchDevice,
} from './gameCore.js';

import { initTouchControls } from './gameTouchControls.js';
import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";
import { openAIPlayWebsocket } from "./websockets.js";

export async function init() {
    try {
        await createAIPlay();

        // Ensure match_id is set
        const match_id = sessionStorage.getItem("match_id");
        if (!match_id) {
            throw new Error("Match ID is not set in sessionStorage.");
        }

        // Change URL to AI mode below
        let data = await apiCallAuthed(`/api/user/aimatch/${match_id}`);

        startCountdown();
        initGameData(data);
        initEventListeners();
        initAIData(data);
        initPaddleEventDispatch();
        drawTick();
        if (isTouchDevice) {
            await delay(100);
            initTouchControls(player1Data);
            console.log("TOUCH CONTROLS ENABLED");
        }
        // Replay disabled (needs to be reworked first)
        replayButton.style.display = "none";
    } catch (error) {
        console.error("Error initializing AI match:", error);
        alert("An error occurred while initializing the AI match.");
    }
}

async function initAIData(data) {
	await fetchCreatorData(data);

	setPlayer1Name(player1Data.username);
	// Set a custom user name for the AI
	setPlayer2Name("Pongothon-9000");

	textDynamicLoad("player1Name", `${player1.name}`);
	textDynamicLoad("player2Name", `${player2.name}`);
	
	if (player1Data.avatar != null)
		player1AvatarPlaceholder.src = player1Data.avatar;

	// Set a custom user image for the AI
	// player2AvatarPlaceholder.src = player2Data.avatar;
}

// Create an AI match
async function createAIPlay(event) {
	try {
		const response = await apiCallAuthed(`/api/ai/match`, "POST", null, null);
		console.log("AI PLAY ID ", response.match_id);
		sessionStorage.setItem("match_id", response.match_id);
		openAIPlayWebsocket(response.match_id);
	} catch (error) {
		console.error("Error creating AI match:", error);
		alert("An error occurred while creating a AI match.");
	}
}