import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";
import { showToast } from "./notifications.js";

let stats;

let friendlistList;
let outgoingList;
let incomingList;
let friendRequestToastElement;
let friendRequestToast;
let friendAddForm;
let friendAddInput;

let matchhistList;
let filterAiBtn;
let filterAiCounter;
let filterLocalBtn;
let filterLocalCounter;
let filterRemoteBtn;
let filterRemoteCounter;

export async function init(data) {

	stats = await apiCallAuthed('/api/user/win-loss');
	textDynamicLoad("userName", `🏓 ${data.username}`);
	textDynamicLoad("numOfWins", `👍 ${stats.overall_win}`);
	textDynamicLoad("numOfLosses", `👎 ${stats.overall_loss}`);
	if (data.avatar != null)
		document.getElementById('profilePic').src = data.avatar;
	
	handleProfilePicUpload();
	handle2FA(data);
	handleUsernameEdit();
	handleCustomColors();

	handleMatchHistory();
	handleFriendlist();
}

// Show a user's profile
async function showUserProfile(event) {
	if (event.target && event.target.matches('a[data-user-id]')) {
		const userId = event.target.getAttribute('data-user-id');
		apiCallAuthed(`/api/user/${userId}/info`)
			.then(response => {
				const userProfile = document.getElementById("userProfileBody");
				userProfile.innerHTML = `
					<img class="profilePic" src="${response.avatar}" alt="User profile picture">
					<div class="text-center fs-3 pb-2">${response.username}</div>
				`;
				// console.log(response);
			})
			.catch(error => {
				console.error('Error showing user profile:', error);
			});
	}
}

function handleMatchHistory() {
	matchhistList = document.getElementById("matchHistoryList");
	filterAiBtn = document.getElementById("filterAiBtn");
	filterAiCounter = document.getElementById("filterAiCounter");
	filterLocalBtn = document.getElementById("filterLocalBtn");
	filterLocalCounter = document.getElementById("filterLocalCounter");
	filterRemoteBtn = document.getElementById("filterRemoteBtn");
	filterRemoteCounter = document.getElementById("filterRemoteCounter");

	filterAiBtn.addEventListener("click", () => {
		listMatchHistory("ai_matches");
	})

	filterLocalBtn.addEventListener("click", () => {
		listMatchHistory("local_matches");
	})

	filterRemoteBtn.addEventListener("click", () => {
		listMatchHistory("remote_matches");
	})

	matchhistList.addEventListener("click", (e) => {
		showUserProfile(e);
	})

	listMatchHistory("ai_matches");
}

async function listMatchHistory(type) {
	try {
		const matchhistReturn = await apiCallAuthed("/api/user/match-history");

		filterAiCounter.innerHTML = matchhistReturn.ai_matches.length || 0;
		filterLocalCounter.innerHTML = matchhistReturn.local_matches.length || 0;
		filterRemoteCounter.innerHTML = matchhistReturn.remote_matches.length || 0;

		const matches = matchhistReturn[type];

		if (!matches || matches.length === 0)
			matchhistList.innerHTML = `<li class="list-group-item text-center">You haven't played any games yet!</li>`;
		else
		{
			matchhistList.innerHTML = '';
			matches.reverse().forEach(match => {
				const listItem = document.createElement('li');
				let decision;
				let opponent_name;
				if ((match.type == "AIMatch" || match.type == "LocalMatch") && (match.player1_score > match.player2_score))
					decision = "👍 WIN"
				else
					decision = "👎 LOSS"
				opponent_name = match.player2_username;
				if (match.type == "RemoteMatch")
				{
					opponent_name = sessionStorage.getItem("id") == match.player1_id ? match.player2_username : match.player1_username;
					const opponent_id = sessionStorage.getItem("id") == match.player1_id ? match.player2_id : match.player1_id;
					opponent_name = `<a class="link-prg" data-bs-toggle="modal" data-bs-target="#userProfileModal" data-user-id=${opponent_id}>${opponent_name}</a>`;
					const ourPlayersScore = sessionStorage.getItem("id") == match.player1_id ? match.player1_score : match.player2_score;
					if (ourPlayersScore == 3)
						decision = "👍 WIN"
					else
						decision = "👎 LOSS"
				}
				listItem.className = 'list-group-item list-group-item-active d-flex w-100 justify-content-between';
				listItem.innerHTML = `
					<p class="mb-1"><strong>${decision}</strong> vs <strong>${opponent_name}</strong></p>
					<small>${match.date.substring(8, 10)}/${match.date.substring(5, 7)}</small>
				`;
				matchhistList.appendChild(listItem);
			});
		}
	} catch (error) {
		console.error('Error fetching match history:', error);
	}
}

function handleCustomColors(){
	let colorLeftPaddle = document.getElementById('colorLeftPaddle');
	let colorRightPaddle = document.getElementById('colorRightPaddle');
	let colorBall = document.getElementById('colorBall');

	colorLeftPaddle.value = localStorage.getItem(`${sessionStorage.getItem("id")}_colorLeftPaddle`) || '#00babc';
	colorRightPaddle.value = localStorage.getItem(`${sessionStorage.getItem("id")}_colorRightPaddle`) || '#df2af7';
	colorBall.value = localStorage.getItem(`${sessionStorage.getItem("id")}_colorBall`) || '#ffffff';

	colorLeftPaddle.addEventListener('input', () => {
		localStorage.setItem(`${sessionStorage.getItem("id")}_colorLeftPaddle`, colorLeftPaddle.value);
	});

	colorRightPaddle.addEventListener('input', () => {
		localStorage.setItem(`${sessionStorage.getItem("id")}_colorRightPaddle`, colorRightPaddle.value);
	});

	colorBall.addEventListener('input', () => {
		localStorage.setItem(`${sessionStorage.getItem("id")}_colorBall`, colorBall.value);
	});

	// Change colors in the main menu animation
	// const root = document.documentElement;
	// root.style.setProperty('--color-left-paddle', colorLeftPaddle.value);
	// root.style.setProperty('--color-right-paddle', colorRightPaddle.value);
	// root.style.setProperty('--color-ball', colorBall.value);
}

function handleFriendlist(){
	outgoingList = document.getElementById("outgoingFriendList");
	incomingList = document.getElementById("incomingFriendList");
	friendlistList = document.getElementById("friendlistList");
	friendAddForm = document.getElementById("friendAddForm");
	friendAddInput = document.getElementById("friendAddInput");
	friendRequestToastElement = document.getElementById('friendRequestToast');
	friendRequestToast = new bootstrap.Toast(friendRequestToastElement);
	listOutgoing();
	listIncoming();
	listFriends();

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
		if (window.location.hash !== '#profile') {
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
				let status;
				if (friend.friend_status == "ON")
					status = "🟢";
				else if (friend.friend_status == "OFF")
					status = "🔴";
				listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
				listItem.innerHTML = `
				${status} ${friend.friend_username}
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

async function handleUsernameEdit() {
	const editUsernameForm = document.getElementById("editUsernameForm");
	const minLength = 3;
	const maxLength = 25;

	editUsernameForm.addEventListener('submit', async () => {
		const editUsernameInput = document.getElementById("editUsernameInput");
		try {
			if (editUsernameInput.value.length < minLength)
				throw("Your username must be atleast 3 characters long.");
			else if (editUsernameInput.value.length > maxLength)
				throw("Your username mustn't be more than 25 characters long.");
			const payload = {'username': editUsernameInput.value};
			await apiCallAuthed("api/user/info", "PUT", undefined, payload);
			textDynamicLoad("userName", `🏓 ${editUsernameInput.value}`);
			showToast('Username Change Successful', `Your username is now ${editUsernameInput.value}.`);
		} catch (error) {
			console.error("Error submitting new username:", error);
			showToast('Username Change Error', error);
		}
	})
}

async function handle2FA(data) {
	const generateBtn = document.getElementById('generateQrCodeButton');
	const qrCodeImage = document.getElementById('qrCodeImage');
	const qrCodeContainer = document.getElementById('qrCodeContainer');
	const multifactorEnableForm = document.getElementById('2faFormEnable');
	const multifactorDisableForm = document.getElementById('2faFormDisable');

	if (!data.two_factor)
	{
		multifactorEnableForm.style.display = "block";
		multifactorDisableForm.style.display = "none";
	}
	else
	{
		multifactorEnableForm.style.display = "none";
		multifactorDisableForm.style.display = "block";
	}

	// QR code generation
	generateBtn.addEventListener('click', async () => {
		try {
			const response = await apiCallAuthed("api/user/2fa-enable", "GET");
			qrCodeImage.src = response.qr_code;
			qrCodeContainer.style.display = 'block';
		} catch (error) {
			console.error("Error generating QR code:", error);
			alert("An error occurred while generating the QR code.");
		}
	});

	multifactorEnableForm.addEventListener('submit', async (event) => {
		event.preventDefault();
		const pin = document.getElementById('pairingPinInputEnable').value;
		try {
			const headers = {
				'Content-Type': 'application/json'
			};
			const payload = {'otp_code': pin};
			await apiCallAuthed("api/user/2fa-enable", "POST", headers, payload);
			alert("2FA Enabled.");
		} catch (error) {
			console.error("Error submitting PIN code:", error);
			alert("An error occurred while submitting the PIN code.");
		}
	});

	multifactorDisableForm.addEventListener('submit', async (event) => {
		event.preventDefault();
		const pin = document.getElementById('pairingPinInputDisable').value;
		try {
			const headers = {
				'Content-Type': 'application/json'
			};
			const payload = {'otp_code': pin};
			await apiCallAuthed("api/user/2fa-disable", "POST", headers, payload);
			alert("2FA Disabled.");
		} catch (error) {
			console.error("Error submitting PIN code:", error);
			alert("An error occurred while submitting the PIN code.");
		}
	});
}

async function handleProfilePicUpload() {
	const editProfilePicForm = document.getElementById("editProfilePicForm");
	const profilePicInput = document.getElementById("profilePicInput");
	const profilePic = document.getElementsByName("profilePic");

	editProfilePicForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		// Check if a file was uploaded
		const file = profilePicInput.files[0];
		if (!file) {
			alert("Please select a file.");
			return;
		}

		// Create a temporary URL
		const img = new Image();
		img.src = URL.createObjectURL(file);

		img.onload = async () => {
			// Check pic dimensions
			if (img.width > 800 || img.height > 800) {
				alert("Image dimensions should not exceed 800x800px.");
				return;
			}
			// Convert img to Base64
			const base64String = await convertToBase64(file);
			// Upload image via API
			try {
				const headers = {
					'Content-Type': 'application/json'
				};
				const payload = { 'profilePic': base64String};
				const response = await apiCallAuthed("api/user/avatar", "PUT", headers, payload);
				console.log("PICTURE SUCCESSFULLY UPLOADED", response);
				location.reload();
				data = await apiCallAuthed('/api/user/info');
				if (data.avatar != null)
					profilePic.src = data.avatar;
			} catch (error) {
				console.error("Error uploading profile picture:", error);
				alert("An error occurred while uploading the profile picture.");
			}
		};
		img.onerror = () => {
			alert("Invalid image file.");
		};
	});
}

function convertToBase64(file) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = error => reject(error);
	});
}