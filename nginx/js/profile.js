import { apiCallAuthed } from './api.js';
import { textDynamicLoad } from "./animations.js";

export function init(data) {
	// LOAD DYNAMIC DATA
	textDynamicLoad("userName", `🏓 ${data.username}`);
	textDynamicLoad("numOfWins", `👍 ${data.win_count}`);
	textDynamicLoad("numOfLosses", `👎 ${data.loss_count}`);
	if (data.avatar != null)
		document.getElementById('profilePic').src = data.avatar;
	
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
					'Content-Type': 'application/json'
				};
				const payload = { 'profilePic': base64String};
				const response = await apiCallAuthed("api/user/avatar", "PUT", headers, payload);
				console.log("PICTURE SUCCESSFULLY UPLOADED", response);
				location.reload();
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