const mockData = {
	profile: {
		user: 'Pepa Vomáčka',
		stats: {
			gamesPlayed: 10,
			wins: 7,
			losses: 3
		}
	},
	game: {
		players: ['John Doe', 'Jane Smith'],
		score: [3, 2]
	}
};

const fetchMockData = (route) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            if (route === '#dashboard') {
                resolve(mockData.profile);
            } else if (route === '#profile') {
                resolve(mockData.profile);
			} else if (route === '#game') {
				resolve(mockData.game);
            } else {
                resolve(null);
            }
        }, 200); // Simulate network delay
    });
};