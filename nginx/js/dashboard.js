import { textDynamicLoad } from "./animations.js";
import { logout } from "./router.js";
import { apiCallAuthed } from "./api.js";

let friendlistBtn;
let friendlistList;
let logoutBtn;

let friendRequestToastElement;
let friendRequestToast;

let friendAddForm;
let friendAddInput;

export async function init(data) {
	sessionStorage.setItem("id", data.id);

	friendlistBtn = document.getElementById("friendlistButton");
	friendlistList = document.getElementById("friendlistList");
	logoutBtn = document.getElementById("logoutButton");

	friendAddForm = document.getElementById("friendAddForm");
	friendAddInput = document.getElementById("friendAddInput");

	friendRequestToastElement = document.getElementById('friendRequestToast');
	friendRequestToast = new bootstrap.Toast(friendRequestToastElement);

	await apiCallAuthed('/api/user/users-list');
	await apiCallAuthed('/api/user/friends');
	await apiCallAuthed('/api/user/friends/sent');
	await apiCallAuthed('/api/user/friends/received');

	// Load dynamic data
	textDynamicLoad("userName", `🏓 ${data.username}`);
	textDynamicLoad("numOfWins", `👍 ${data.win_count}`);
	textDynamicLoad("numOfLosses", `👎 ${data.loss_count}`);
	if (data.avatar != null)
		document.getElementById('profilePic').src = data.avatar;

	// Add selected game mode to local storage
	document.querySelectorAll('#menu a').forEach(link => {
		link.addEventListener('click', function() {
			const mode = this.getAttribute('data-mode');
			localStorage.setItem('gameMode', mode);
		});
	});

	// Logout button
	logoutBtn.addEventListener('click', (event) => {
		event.preventDefault();
		logout();
	});

	// Friendlist button
	friendlistBtn.addEventListener('click', (event) => {
		event.preventDefault();
		listFriends();
	});

	// Friend add request
	friendAddForm.addEventListener('submit', (event) => {
		event.preventDefault();
		addFriend(friendAddInput.value);
	});
}

// List friends
async function listFriends() {
	try {
		const friendlistReturn = await apiCallAuthed('/api/user/friends', undefined, undefined, undefined, false);

		if (!friendlistReturn || friendlistReturn.length === 0)
			friendlistList.innerHTML = '<li class="list-group-item text-center">You have no friends :(</li>';
		else
		{
			friendlistList.innerHTML = '';
			friendlistReturn.forEach(friend => {
				const listItem = document.createElement('li');
				listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
				listItem.innerHTML = `
				${friend.username}
				`;
				friendlistList.appendChild(listItem);
			});
		}
	} catch (error) {
		console.error('Error fetching friendslist:', error);
	}
}

async function addFriend() {
	try {
		const addRequest = await apiCallAuthed(`/api/user/friends/request/${friendAddInput.value}`);
	}
}