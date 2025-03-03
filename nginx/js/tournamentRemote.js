import { apiCallAuthed, ensureValidAccessToken } from './api.js';
import { openTournamentWebsocket } from './websockets.js';
import { showToast } from "./notifications.js";

let tournamentCreateForm;
let joinableTournaments;
let refreshTournamentsBtn;

export function init() {
	tournamentCreateForm = document.getElementById("create-tournament-form");
	tournamentCreateForm.addEventListener("submit", (e) => createTournament(e));

	joinableTournaments = document.getElementById("joinable-tournaments");

	fetchAndUpdateTournamentList()
	refreshTournamentsBtn = document.getElementById("refreshTournamentsBtn");
	refreshTournamentsBtn.addEventListener("click", fetchAndUpdateTournamentList);

	joinableTournaments.addEventListener('click', (e) => joinTournament(e));

}

// Create a tournament
async function createTournament(event) {
	event.preventDefault();

	const tournamentName = document.getElementById("tournament-name").value;
	const tournamentSlots = document.getElementById("tournament-slots").value;

	try {
		const payload = {
			'tournament_name': tournamentName,
			// 'player_tmp_username': "borecek",
		};

		const response = await apiCallAuthed(`/api/tournament/create/${tournamentSlots}/`, "POST", null, payload);
		// console.log("TOURNAMENT ID, ", response.tournament.id);
		localStorage.setItem("tournament_id", response.tournament.id);
		//openTournamentWebsocket(response.tournament.id);
		window.location.hash = '#lobby-tnmt';
	} catch (error) {
		// console.error("Error creating tournament:", error);
		showToast("Error creating tournament", null, error, "t_tournamentCreationError");
	}
}

// Join a tournament
async function joinTournament(event) {
	if (event.target && event.target.matches('button[data-tournament-id]')) {
		const tournamentId = event.target.getAttribute('data-tournament-id');
		apiCallAuthed(`/api/tournament/join/${tournamentId}/`, "POST")
			.then(response => {
				//openTournamentWebsocket(response.tournament.id);
				localStorage.setItem("tournament_id", tournamentId);
				window.location.hash = '#lobby-tnmt';
			})
			.catch(error => {
				// console.error('Error joining tournament:', error);
				showToast("Error joining tournament", null, error, "t_tournamentJoinError");
			});
	}
}

// List available tournaments
async function fetchAndUpdateTournamentList() {
	try {
		await ensureValidAccessToken();
		const tournamentList = await apiCallAuthed('api/tournament/list/waiting', undefined, undefined, undefined, false);

		if (!tournamentList || tournamentList.length === 0)
			joinableTournaments.innerHTML = '<li class="list-group-item text-center">No available tournaments</li>';
		else
		{
			joinableTournaments.innerHTML = '';
			tournamentList.forEach(tournament => {
				if (tournament.free_spaces != 0)
				{
					const listItem = document.createElement('li');
					listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
					listItem.innerHTML = `
					${tournament.name}
					<button class="btn btn-prg btn-sm" data-translate="tournamentJoinButton" data-tournament-id="${tournament.id}">Join</button>
					`;
					joinableTournaments.appendChild(listItem);
				}
			});
		}
	} catch (error) {
		// console.error('Error fetching player list:', error);
	}
}