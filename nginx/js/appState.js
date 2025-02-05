const appState = {
	loggedIn: false,
	isLoggingOut: false,
	accessToken: localStorage.getItem('access'),
	matchId: localStorage.getItem('match_id'),
	tournamentId: localStorage.getItem('tournament_id'),
}

export default appState;