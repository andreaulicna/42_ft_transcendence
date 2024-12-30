import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";
import { showToast } from "./notifications.js";

export function init(data) {
	textDynamicLoad("userName", `🏓 ${data.username}`);
	textDynamicLoad("numOfWins", `👍 ${data.win_count}`);
	textDynamicLoad("numOfLosses", `👎 ${data.loss_count}`);
	if (data.avatar != null)
		document.getElementById('profilePic').src = data.avatar;
	
	handleProfilePicUpload();
	handle2FA(data);
	handleUsernameEdit();
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