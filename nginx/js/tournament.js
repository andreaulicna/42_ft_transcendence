import { apiCallAuthed } from './api.js';

export function init() {
	// CREATE TOURNAMENT
	const tournamentCreateForm = document.getElementById("create-tournament-form");
	const tournamentJoinRandom = document.getElementById("join-random-tournament-btn");

	tournamentCreateForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		const tournamentName = document.getElementById("tournament-name").value;
		// const tournamentSlots = document.getElementById("tournament-slots").value;

		try {
			// const headers = {
			// 	'Content-Type': 'application/json',
			// };

			// const payload = JSON.stringify({
			// 	tournament_name: tournamentName,
			// 	player_tmp_username: "borecek",
			// });

			const response = await apiCallAuthed("/api/tournament/create", "POST");
			console.log("Tournament created", response);
			window.location.hash = '#lobby';
		} catch (error) {
			console.error("Error creating tournament:", error);
			alert("An error occurred while creating a tournament.");
		}
		
	});

	tournamentJoinRandom.addEventListener("click", async (event) => {
		event.preventDefault();

		try {
			// const headers = {
			// 	'Content-Type': 'application/json',
			// };

			// const payload = JSON.stringify({
			// 	tournament_name: tournamentName,
			// 	player_tmp_username: "borecek",
			// });

			const response = await apiCallAuthed("/api/tournament/join", "POST");
			console.log("Tournament joined", response);
			window.location.hash = '#lobby';
		} catch (error) {
			console.error("Error joining tournament:", error);
			alert("An error occurred while joining a tournament.");
		}
		
	});
}