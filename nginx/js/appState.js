window.appState = {
	loggedIn: false,
	isLoggingOut: false,
	loginPayloadFor2FA: null,
	accessToken: localStorage.getItem('access'),
	matchId: localStorage.getItem('match_id'),
	tournamentId: localStorage.getItem('tournament_id'),
}