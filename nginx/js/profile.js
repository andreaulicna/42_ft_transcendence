export function init(data) {
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.user;
	document.getElementById('numOfPlayed').textContent = '⚔️ ' + data.stats.gamesPlayed;
	document.getElementById('numOfWins').textContent = '👍 ' + data.stats.wins;
	document.getElementById('numOfLosses').textContent = '👎 ' + data.stats.losses;
}