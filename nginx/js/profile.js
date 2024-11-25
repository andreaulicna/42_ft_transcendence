import { apiCallAuthed } from './api.js';

export function init(data) {
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.username;
	document.getElementById('numOfWins').textContent = '👍 ' + data.win_count;
	document.getElementById('numOfLosses').textContent = '👎 ' + data.loss_count;

	// HANDLE PROFILE PIC UPLOAD
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
					'Content-Type': 'application/json',
				};
				const payload = JSON.stringify({ profilePic: base64String });
				const response = await apiCallAuthed("api/user/avatar", "PUT", headers, payload);
				if (response.ok) {
					profilePic.src = base64String;
				} else {
					alert("Failed to upload profile picture.");
				}
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

// FILE TO BASE64 CONVERSION
function convertToBase64(file) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => resolve(reader.result);
		reader.onerror = error => reject(error);
	});
}