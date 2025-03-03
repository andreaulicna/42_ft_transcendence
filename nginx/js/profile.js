import { apiCallAuthed, ensureValidAccessToken } from './api.js';
import { textDynamicLoad } from "./animations.js";
import { showToast } from "./notifications.js";

let stats;

let friendlistList;
let outgoingList;
let incomingList;
let friendAddForm;
let friendAddInput;

let matchhistList;
let filterAiBtn;
let filterAiCounter;
let filterLocalBtn;
let filterLocalCounter;
let filterRemoteBtn;
let filterRemoteCounter;

let resetColorsBtn;

export async function init(data) {

	stats = await apiCallAuthed('/api/user/win-loss');
	textDynamicLoad("userName", `${data.username}`);
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

	resetColorsBtn = document.getElementById("resetColorsButton");
	resetColorsBtn.addEventListener("click", resetColors);
}

function resetColors()
{
	let colorLeftPaddle = document.getElementById('colorLeftPaddle');
	let colorRightPaddle = document.getElementById('colorRightPaddle');
	let colorBall = document.getElementById('colorBall');

	localStorage.removeItem(`${localStorage.getItem("id")}_colorLeftPaddle`);
	localStorage.removeItem(`${localStorage.getItem("id")}_colorRightPaddle`);
	localStorage.removeItem(`${localStorage.getItem("id")}_colorBall`);

	colorLeftPaddle.value = '#00babc';
	colorRightPaddle.value = '#df2af7';
	colorBall.value = '#ffffff';
}

// Show a user's profile
async function showUserProfile(event) {
	if (event.target && event.target.matches('a[data-user-id]')) {
		const userId = event.target.getAttribute('data-user-id');
		apiCallAuthed(`/api/user/${userId}/info`)
			.then(response => {
				const userProfile = document.getElementById("userProfileBody");
				const userAvatar = response.avatar || "assets/default_user_pfp.png";
				userProfile.innerHTML = `
					<img class="profilePic" src="${userAvatar}" alt="User profile picture">
					<div class="text-center fs-3 pb-2">${response.username}</div>
					<button type="button" id="addInspectedFriendBtn" class="btn btn-prg" data-translate="addFriend">Add Friend</button>
				`;

				const addUserBtn = document.getElementById("addInspectedFriendBtn");
				addUserBtn.addEventListener("click", () => {
					addFriend(response.username)
				})
			})
			.catch(error => {
				// console.error('Error showing user profile:', error);
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
			matchhistList.innerHTML = `<li class="list-group-item text-center" data-translate="noGamesYet">You haven't played any games yet!</li>`;
		else
		{
			matchhistList.innerHTML = '';
			matches.reverse().forEach(match => {
				const listItem = document.createElement('li');
				let p1 = match.player1_username;
				let p2 = match.player2_username;
				if (match.type == "RemoteMatch")
				{
					if (localStorage.getItem("id") == match.player1_id)
						p2 = `<a class="link-prg" data-bs-toggle="modal" data-bs-target="#userProfileModal" data-user-id=${match.player2_id}>${match.player2_username}</a>`;
					else
						p1 = `<a class="link-prg" data-bs-toggle="modal" data-bs-target="#userProfileModal" data-user-id=${match.player1_id}>${match.player1_username}</a>`;
				}
				listItem.className = 'list-group-item list-group-item-active d-flex w-100 justify-content-between';
				listItem.innerHTML = `
					<span class="mb-1"><strong>${match.player1_score} : ${match.player2_score}</strong></span>
					<span>${p1} vs. ${p2}</span>
					<small>${match.date.substring(8, 10)}/${match.date.substring(5, 7)}</small>
				`;
				matchhistList.appendChild(listItem);
			});
		}
	} catch (error) {
		// console.error('Error fetching match history:', error);
	}
}

function handleCustomColors() {
	let colorLeftPaddle = document.getElementById('colorLeftPaddle');
	let colorRightPaddle = document.getElementById('colorRightPaddle');
	let colorBall = document.getElementById('colorBall');

	colorLeftPaddle.value = localStorage.getItem(`${localStorage.getItem("id")}_colorLeftPaddle`) || '#00babc';
	colorRightPaddle.value = localStorage.getItem(`${localStorage.getItem("id")}_colorRightPaddle`) || '#df2af7';
	colorBall.value = localStorage.getItem(`${localStorage.getItem("id")}_colorBall`) || '#ffffff';

	colorLeftPaddle.addEventListener('input', () => {
		localStorage.setItem(`${localStorage.getItem("id")}_colorLeftPaddle`, colorLeftPaddle.value);
	});

	colorRightPaddle.addEventListener('input', () => {
		localStorage.setItem(`${localStorage.getItem("id")}_colorRightPaddle`, colorRightPaddle.value);
	});

	colorBall.addEventListener('input', () => {
		localStorage.setItem(`${localStorage.getItem("id")}_colorBall`, colorBall.value);
	});
}

async function handleFriendlist() {
	outgoingList = document.getElementById("outgoingFriendList");
	incomingList = document.getElementById("incomingFriendList");
	friendlistList = document.getElementById("friendlistList");
	friendAddForm = document.getElementById("friendAddForm");
	friendAddInput = document.getElementById("friendAddInput");
	const refreshFriendlistBtn = document.getElementById("refreshFriendlistBtn");

	await ensureValidAccessToken();
	listOutgoing();
	listIncoming();
	listFriends();

	// Friend add request
	friendAddForm.addEventListener('submit', (event) => {
		event.preventDefault();
		addFriend(friendAddInput.value);
	});

	refreshFriendlistBtn.addEventListener("click", async () => {
		await ensureValidAccessToken();
		listOutgoing();
		listIncoming();
		listFriends();
	});
}


// List outgoing friend requests
async function listOutgoing() {
	try {
		const outgoingReturn = await apiCallAuthed('/api/user/friends/sent', undefined, undefined, undefined, false);

		if (!outgoingReturn || outgoingReturn.length === 0)
			outgoingList.innerHTML = '<li class="list-group-item text-center" data-translate="noOutgoingRequests">You have no outgoing friend requests.</li>';
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
		// console.error('Error fetching outgoing friend requests:', error);
	}
}

// List incoming friend requests
async function listIncoming() {
	try {
		const incomingReturn = await apiCallAuthed('/api/user/friends/received', undefined, undefined, undefined, false);

		if (!incomingReturn || incomingReturn.length === 0)
			incomingList.innerHTML = '<li class="list-group-item text-center" data-translate="noIncomingRequests">You have no incoming friend requests.</li>';
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
		// console.error('Error fetching incoming friend requests:', error);
	}
}

async function handleAccept(event) {
	const requestId = event.target.getAttribute('data-request-id');
	try {
		await apiCallAuthed(`/api/user/friends/${requestId}/accept`, 'POST');
		showToast('Friend Request Accepted', 'You have accepted the friend request.', null, "t_requestAccept");
		listIncoming();
		listFriends();
	} catch (error) {
		// console.error('Error accepting friend request:', error);
		showToast('Error accepting friend request', null, error, "t_requestAcceptError");
	}
}

async function handleReject(event) {
	const requestId = event.target.getAttribute('data-request-id');
	try {
		await apiCallAuthed(`/api/user/friends/${requestId}/refuse`, 'POST');
		showToast('Friend Request Rejected', 'You have rejected the friend request.', null, "t_requestReject");
		listIncoming(); // Refresh the list
	} catch (error) {
		// console.error('Error rejecting friend request:', error);
		showToast('Error rejecting friend request', null, error, "t_requestRejectError");
	}
}

// List friends
let friends = [];

async function listFriends() {
	try {
		const friendlistReturn = await apiCallAuthed('/api/user/friends', undefined, undefined, undefined, false);

		if (!friendlistReturn || friendlistReturn.length === 0) {
			friendlistList.innerHTML = '<li class="list-group-item text-center" data-translate="noFriends">You have no friends :(</li>';
		} else {
			friendlistList.innerHTML = '';
			friends = friendlistReturn; // Store the friend list
			friendlistReturn.forEach(friend => {
				const listItem = document.createElement('li');
				let statusIcon = friend.friend_status === "ON" ? "🟢" : "🔴";
				listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
				listItem.innerHTML = `
				<div>
					<span class="status-icon">${statusIcon}</span>
					<span class="friend-username" data-user-id="${friend.friend_id}">${friend.friend_username}</span>
				</div>
				<button type="button" class="btn btn-prg friendDeleteButton" data-request-id="${friend.id}">
					❌
				</button>
				`;
				friendlistList.appendChild(listItem);
			});

			document.querySelectorAll('.friendDeleteButton').forEach(button => {
				button.addEventListener('click', handleDeleteFriend);
			});
		}
	} catch (error) {
		// console.error('Error fetching friendslist:', error);
	}
}

async function handleDeleteFriend(event) {
	const requestId = event.target.getAttribute('data-request-id');
	try {
		await apiCallAuthed(`/api/user/friends/${requestId}/delete`, 'DELETE');
		showToast('Friend Deleted', 'You have deleted a friend from the list.', null, "t_friendDelete");
		listFriends(); // Refresh the list
	} catch (error) {
		// console.error('Error deleting friend:', error);
		showToast('Error deleting friend', null, error, "t_friendDeleteError");
	}
}

// Find the friend in the list and update their status with data from the Status websocket
export function handleFriendStatusUpdate(data) {
	const { id, status, username } = data;

	const friend = friends.find(friend => friend.friend_id === id);
	if (friend) {
		friend.friend_status = status;

		// Update the DOM
		const findFriend = Array.from(friendlistList.children);
		let listItem;
		if (findFriend)
			listItem = findFriend.find(item => item.querySelector('.friend-username').getAttribute('data-user-id') == id);
		if (listItem)
		{
			let statusIcon = status === "ON" ? "🟢" : "🔴";
			const statusIconElement = listItem.querySelector('.status-icon');
			if (statusIconElement)
				statusIconElement.textContent = statusIcon;
			const friendNameElement = listItem.querySelector('.friend-username');
			if (friendNameElement)
				friendNameElement.textContent = username;
		}
	}
}

async function addFriend(username) {
	try {
		const addRequest = await apiCallAuthed(`/api/user/friends/request/${username}`, "POST");
		listOutgoing();
		showToast('Friend Request', `Friend request sent.`, null, "t_requestSent");
		if (friendAddInput.value)
			friendAddInput.value="";
	} catch (error) {
		// console.error('Error adding friend:', error);
		showToast('Error adding friend', null, error, "t_requestSentError");
	}
}

async function handleUsernameEdit() {
	const editUsernameForm = document.getElementById("editUsernameForm");

	editUsernameForm.addEventListener('submit', async (event) => {
		event.preventDefault();
		const editUsernameInput = document.getElementById("editUsernameInput");
		try {
			const payload = {'username': editUsernameInput.value};
			await apiCallAuthed("api/user/info", "PUT", undefined, payload);
			textDynamicLoad("userName", `${editUsernameInput.value}`);
			showToast('Username Change Successful', `You have updated your username.`, null, "t_nameChange");
		} catch (error) {
			// console.error("Error submitting new username:", error);
			showToast('Username Change Error', null, error, "t_nameChangeError");
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
			// console.error("Error generating QR code:", error);
			showToast("Error generating QR code", null, error, "t_qrGenError");
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
			showToast("2FA", "The 2FA settings for this account has been enabled.", null, "t_2faEnable");
		} catch (error) {
			// console.error("Error submitting PIN code:", error);
			showToast("Error submitting PIN code", null, error, "t_pinSubmitError");
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
			showToast("2FA", "The 2FA settings for this account has been disabled.", null, "t_2faDisable");
		} catch (error) {
			// console.error("Error submitting PIN code:", error);
			showToast("Error submitting PIN code", null, error, "t_pinSubmitError");
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
			showToast("Error", "Please select a file.", null, "t_selectFileError");
			return;
		}

		// Create a temporary URL
		const img = new Image();
		img.src = URL.createObjectURL(file);

		img.onload = async () => {
			// Check pic dimensions
			if (img.width > 800 || img.height > 800) {
				showToast("Error", "Image dimensions should not exceed 800x800 px.", null, "t_imageDimensionsError");
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
				// console.log("PICTURE SUCCESSFULLY UPLOADED", response);
				location.reload();
				data = await apiCallAuthed('/api/user/info');
				if (data.avatar != null)
					profilePic.src = data.avatar;
			} catch (error) {
				// console.error("Error uploading profile picture:", error);
				showToast("Error uploading profile picture", null, error, "t_profilePictureUploadError");
			}
		};
		img.onerror = () => {
			showToast("Error", "Invalid image file.", null, "t_invalidImageFileError");
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