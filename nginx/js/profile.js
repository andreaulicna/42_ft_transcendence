export function init(data) {
	// LOAD DYNAMIC DATA
	document.getElementById('userName').textContent = '🏓 ' + data.user;
	document.getElementById('numOfPlayed').textContent = '⚔️ ' + data.stats.gamesPlayed;
	document.getElementById('numOfWins').textContent = '👍 ' + data.stats.wins;
	document.getElementById('numOfLosses').textContent = '👎 ' + data.stats.losses;

	// HANDLE PROFILE PIC UPLOAD
	const editProfilePicForm = document.getElementById("editProfilePicForm");
	const profilePicInput = document.getElementById("profilePicInput");
	const profilePic = document.getElementsByName("profilePic");

	editProfilePicForm.addEventListener("submit", async (event) => {
		event.preventDefault();

		const file = profilePicInput.files[0];
		if (!file) {
			alert("Please select a file.");
			return;
		}

		const img = new Image();
		img.src = URL.createObjectURL(file);

		img.onload = async () => {
			if (img.width > 800 || img.height > 800) {
				alert("Image dimensions should not exceed 800x800px.");
				return;
			}

			const formData = new FormData();
			formData.append("profilePic", file);

			try {
				// TADY NAHRADIT URL :)
				const response = await fetch("https://run.mocky.io/v3/6a954489-1ac3-4f46-806c-ddd06f625420", {
					method: "POST",
					body: formData
				});

				if (response.ok) {
					alert("Profile picture updated successfully.");
					profilePic.src = URL.createObjectURL(file);
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