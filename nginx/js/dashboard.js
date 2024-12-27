import { textDynamicLoad } from "./animations.js";
import { showToast } from "./notifications.js";
import { logout } from "./router.js";
import { apiCallAuthed } from "./api.js";

let friendlistBtn;
let friendlistList;
let outgoingList;
let incomingList;
let logoutBtn;

let friendRequestToastElement;
let friendRequestToast;

let friendAddForm;
let friendAddInput;

export async function init(data) {
	sessionStorage.setItem("id", data.id);

	friendlistBtn = document.getElementById("friendlistButton");
	outgoingList = document.getElementById("outgoingFriendList");
	incomingList = document.getElementById("incomingFriendList");
	friendlistList = document.getElementById("friendlistList");
	logoutBtn = document.getElementById("logoutButton");

	friendAddForm = document.getElementById("friendAddForm");
	friendAddInput = document.getElementById("friendAddInput");

	friendRequestToastElement = document.getElementById('friendRequestToast');
	friendRequestToast = new bootstrap.Toast(friendRequestToastElement);

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

	// Friendlist buttony
	friendlistBtn.addEventListener('click', (event) => {
		event.preventDefault();
		listOutgoing();
		listIncoming();
		listFriends();
	});

	// Friend add request
	friendAddForm.addEventListener('submit', (event) => {
		event.preventDefault();
		addFriend(friendAddInput.value);
	});

	// Refresh friendlist
	fetchAndUpdateFriendList()
	let refreshInterval = setInterval(fetchAndUpdateFriendList, 3000);
	
	// Clear the list refresh interval when the user exits the page
	window.addEventListener('hashchange', () => {
		if (window.location.hash !== '#dashboard') {
			clearInterval(refreshInterval);
		}
	});
}

function fetchAndUpdateFriendList() {
	listOutgoing();
	listIncoming();
	listFriends();
}

// List outgoing friend requests
async function listOutgoing() {
	try {
		const outgoingReturn = await apiCallAuthed('/api/user/friends/sent', undefined, undefined, undefined, false);

		if (!outgoingReturn || outgoingReturn.length === 0)
			outgoingList.innerHTML = '<li class="list-group-item text-center">You have no outgoing friend requests.</li>';
		else
		{
			outgoingList.innerHTML = '';
			outgoingReturn.forEach(request => {
				const listItem = document.createElement('li');
				listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
				listItem.innerHTML = `
				${request.friend_username}
				`;
				outgoingList.appendChild(listItem);
			});
		}
	} catch (error) {
		console.error('Error fetching outgoing friend requests:', error);
	}
}

// List incoming friend requests
async function listIncoming() {
	try {
		const incomingReturn = await apiCallAuthed('/api/user/friends/received', undefined, undefined, undefined, false);

		if (!incomingReturn || incomingReturn.length === 0)
			incomingList.innerHTML = '<li class="list-group-item text-center">You have no incoming friend requests.</li>';
		else
		{
			incomingList.innerHTML = '';
			incomingReturn.forEach(request => {
				const listItem = document.createElement('li');
				listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
				listItem.innerHTML = `
				${request.friend_username}
				<div class="d-flex gap-2">
				<button type="button" class="btn btn-prg friendAcceptButton" data-request-id="${request.id}">
					✅
				</button>
				<button type="button" class="btn btn-prg friendRejectButton" data-request-id="${request.id}">
					❌
				</button>
				</div>
				`;
				incomingList.appendChild(listItem);
			});

			// Add event listeners for accept and reject buttons
			document.querySelectorAll('.friendAcceptButton').forEach(button => {
				button.addEventListener('click', handleAccept);
			});
			document.querySelectorAll('.friendRejectButton').forEach(button => {
				button.addEventListener('click', handleReject);
			});
		}
	} catch (error) {
		console.error('Error fetching incoming friend requests:', error);
	}
}

async function handleAccept(event) {
	const requestId = event.target.getAttribute('data-request-id');
	try {
		await apiCallAuthed(`/api/user/friends/${requestId}/accept`, 'POST');
		showToast('Friend Request Accepted', 'You have accepted the friend request.');
		listIncoming();
		listFriends();
	} catch (error) {
		console.error('Error accepting friend request:', error);
		showToast('Error', 'Failed to accept the friend request.');
	}
}

async function handleReject(event) {
	const requestId = event.target.getAttribute('data-user-id');
	try {
		await apiCallAuthed(`/api/user/friends/${requestId}/refuse`, 'POST');
		showToast('Friend Request Rejected', 'You have rejected the friend request.');
		listIncoming(); // Refresh the list
	} catch (error) {
		console.error('Error rejecting friend request:', error);
		showToast('Error', 'Failed to reject the friend request.');
	}
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
				${friend.friend_username}
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
		const addRequest = await apiCallAuthed(`/api/user/friends/request/${friendAddInput.value}`, "POST");
		showToast('Friend Request', `Friend request to ${friendAddInput.value} sent.`);
	} catch (error) {
		console.error('Error adding friend:', error);
	}
}