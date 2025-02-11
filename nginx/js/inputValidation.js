/* INPUT VALIDATION*/

function setInputValidation(inputElement, customMessages)
{
	const showCustomMessage = () => {
		for (const [validityState, message] of Object.entries(customMessages)) {
			if (inputElement.validity[validityState]) {
				inputElement.setCustomValidity(message);
				return;
			}
		}
		inputElement.setCustomValidity(""); // Clear custom message if input is valid
	};

	inputElement.addEventListener("input", showCustomMessage);
	inputElement.addEventListener("invalid", showCustomMessage);
}

// Apply validation when elements are available
function applyValidationWhenAvailable(selector, customMessages)
{
	const observer = new MutationObserver(() => {
		const inputElement = document.querySelector(selector);
		if (inputElement) {
			setInputValidation(inputElement, customMessages);
			observer.disconnect(); // Stop observing once the element is found and validation is applied
		}
	});

	observer.observe(document.body, { childList: true, subtree: true });
}

// Apply validation on DOMContentLoaded and when elements are dynamically added
document.addEventListener("DOMContentLoaded", () => {
	applyValidationWhenAvailable("#editUsernameInput", {
		patternMismatch: "Please use only letters or numbers (3–20 chars).",
		valueMissing: "Username is required."
	});

	applyValidationWhenAvailable("#local-player1-tmp-username", {
		patternMismatch: "Please use only letters or numbers (3–20 chars).",
		valueMissing: "Player 1's name is required."
	});

	applyValidationWhenAvailable("#local-player2-tmp-username", {
		patternMismatch: "Please use only letters or numbers (3–20 chars).",
		valueMissing: "Player 2's name is required."
	});

	// applyValidationWhenAvailable("#inputUsernameLogin", {
	// 	patternMismatch: "Please use only letters or numbers (3–20 chars).",
	// 	valueMissing: "A username is required."
	// });

	// applyValidationWhenAvailable("#inputPasswordLogin", {
	// 	// patternMismatch: "Password must be 6–20 characters long and can include letters, numbers, and the following symbols: !@#$%&*_?.",
	// 	valueMissing: "A password is required."
	// });

	applyValidationWhenAvailable("#inputUsernameRegister", {
		patternMismatch: "Please use only letters or numbers (3–20 chars).",
		valueMissing: "A username is required."
	});

	applyValidationWhenAvailable("#inputPasswordRegister", {
		patternMismatch: "Password must be 6–20 characters long and can include letters, numbers, and the following symbols: !@#$%&*_?.",
		valueMissing: "A password is required."
	});

	applyValidationWhenAvailable("#friendAddInput", {
		patternMismatch: "A username can only have letters or numbers (3–20 chars).",
		valueMissing: "A username is required."
	});
	
	applyValidationWhenAvailable("#tournament-name", {
		patternMismatch: "The tournament name can only have letters or numbers (3–20 chars).",
		valueMissing: "A tournament name is required."
	});

	applyValidationWhenAvailable("#add-player-form-input", {
		patternMismatch: "A username can only have letters or numbers (3–20 chars).",
		valueMissing: "A username is required."
	});
});