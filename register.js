export function addRegistrationFormListener() {
    const form = document.getElementById('registrationForm');
    if (form) {

        form.addEventListener('submit', async function(event) {
			console.log('hello')
            event.preventDefault(); // Prevent the default form submission

            // Capture the input values
            const email = document.getElementById('inputEmail').value;
            const password = document.getElementById('inputPassword').value;

            // Create the payload
            const payload = {
                username: email,
                password: password
            };

            try {
                // Send the data to the API
                const response = await fetch('http://localhost:1337/api/user/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                // Handle the response
                if (response.ok) {
                    const data = await response.json();
                    console.log('Registration successful:', data);
                    // Optionally, redirect the user or show a success message
                } else {
                    const errorData = await response.json();
                    console.error('Registration failed:', errorData);
                    // Optionally, show an error message to the user
                }
            } catch (error) {
                console.error('Error:', error);
                // Optionally, show an error message to the user
            }
        });
    }
}