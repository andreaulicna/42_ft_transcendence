const routes = {
    '/' : 'login-template',
    '/dashboard' : 'dashboard-template',
    '/game' : 'game-template'
};

const rootDiv = document.getElementById('root');

const onNavigate = (event, pathname) => {
	if (event) {
		event.preventDefault();
	}
    window.history.pushState(
        {},
        pathname,
        window.location.origin + pathname
    );
    renderView(pathname);
};

const renderView = (pathname) => {
    rootDiv.innerHTML = '';
    const template = document.getElementById(routes[pathname]);
    const clone = document.importNode(template.content, true);
    rootDiv.appendChild(clone);

    if (pathname === '/game') {
        initializeGame(); // Initialize the game after injecting the gameBoard element
    };
};

window.onpopstate = () => {
    renderView(window.location.pathname);
};

// Initial render
renderView(window.location.pathname);