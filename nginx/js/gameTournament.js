export function handleTournamentGameOver() {
	matchID = sessionStorage.getItem("match_id");
	tournamentRoundNumber++;
	console.log("ROUND NUMBER", tournamentRoundNumber);
	console.log("MAX ROUNDS", tournamentRoundMax);
	const winnerID = player1.score > player2.score ? player1Data.id : player2Data.id;
	const loserID = player1.score > player2.score ? player2Data.id : player1Data.id;
	if (sessionStorage.getItem("id") == winnerID) {
		dispatchWinnerMatchEnd(winnerID, matchID);
		// if (tournamentRoundNumber >= tournamentRoundMax)
		// 	window.location.hash = "winner-tnmt";
		hideGameOverScreen();
	} else if (sessionStorage.getItem("id") == loserID) {
		closeTournamentWebsocket();
		window.location.hash = '#dashboard';
	}
}

function dispatchWinnerMatchEnd(winnerId, matchId) {
	const message ={
		message: "match_end",
		match_id: matchId,
		winner_id: winnerId
	};
	const event = new CustomEvent('tournamentMatchEnd', { detail: message });
	// console.log("DISPATCHING END MATCH MSG", message);
	window.dispatchEvent(event);
}