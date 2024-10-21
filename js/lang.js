const translations = {
	en: {
		// INDEX
		title: "Transcendence",
		welcome: "Welcome",
		madeBy: "made by 42 Prague students",
		language: "Language",
		// LOGIN
		emailPlaceholder: "Your email address",
		passwordPlaceholder: "Your password",
		loginEmail: "Login with email",
		loginIntra: "Login with Intra",
		loginOr: "or",
		firstTime: "First time here?",
		createAccount: "Make a new account!",
		// DASHBOARD
		modeLocal: "Local Player",
		modeRemote: "Remote Player",
		modeAI: "AI Player",
		modeTournament: "Tournament",
		viewProfile: "Profile",
		// GAME
		hasWon: "has won!",
		buttonReplay: "Replay",
		buttonMenu: "Main Menu",
		// TOURNAMENT
		tournamentCreate: "Create Tournament",
		tournamentName: "Tournament Name",
		tournamentNamePlaceholder: "Enter tournament name",
		tournamentSlots: "Create Tournament",
		tournamentCreateButton: "Create",
		tournamentJoin: "Join Tournament",
		tournamentJoinButton: "Join",
		tournamentLobby: "Lobby for ",
		tournamentLobbyWait: "Waiting for players to join...",
		tournamentLobbyStartButton: "Start Game",
		tournamentLobbyCancelButton: "Cancel Lobby",
		// PROFILE
		tabProfile: "Profile",
		tabMatches: "Match History",
		tabFriendlist: "Friendlist",
		profileAccountName: "Account name",
		profileDisplayName: "Display name",
		editDisplayName: "Edit Display Name",
		editProfilePic: "Edit Profile Picture",
	},
	cz: {
		// INDEX
		title: "Transcendence",
		welcome: "Vítejte",
		madeBy: "vytvořeno studenty 42 Prague",
		language: "Jazyk",
		// LOGIN
		emailPlaceholder: "Vaše emailová adresa",
		passwordPlaceholder: "Vaše heslo",
		loginEmail: "Přihlášení emailem",
		loginIntra: "Přihlášení skrze Intra",
		loginOr: "nebo",
		firstTime: "Jsi tu poprvé?",
		createAccount: "Vytvoř si účet!",
		// DASHBOARD
		modeLocal: "Lokální hráč",
		modeRemote: "Vzdálený hráč",
		modeAI: "AI hráč",
		modeTournament: "Turnaj",
		viewProfile: "Profil",
		// GAME
		hasWon: "je vítěz!",
		buttonReplay: "Hrát znovu",
		buttonMenu: "Hlavní menu",
		// TOURNAMENT
		tournamentCreate: "Vytvoř turnaj",
		tournamentName: "Název turnaje",
		tournamentNamePlaceholder: "Vlož jméno turnaje",
		tournamentSlots: "Počet hráčů",
		tournamentCreateButton: "Vytvořit",
		tournamentJoin: "Přidej se k turnaji",
		tournamentJoinButton: "Připojit",
		tournamentLobby: "Herní lobby pro ",
		tournamentLobbyWait: "Čekání na ostatní hráče...",
		tournamentLobbyStartButton: "Začít hru",
		tournamentLobbyCancelButton: "Zrušit lobby",
		// PROFILE
		tabProfile: "Profil",
		tabMatches: "Historie zápasů",
		tabFriendlist: "Seznam přátel",
		profileAccountName: "Název účtu",
		profileDisplayName: "Přezdívka",
		editDisplayName: "Změnit přezdívku",
		editProfilePic: "Změnit profilový obrázek",
	},
	sk: {
		// INDEX
		title: "Transcendence",
		welcome: "Vitajte",
		madeBy: "vytvorené študentmi 42 Prague",
		language: "Jazyk",
		// LOGIN
		emailPlaceholder: "Vaša emailová adresa",
		passwordPlaceholder: "Vaše heslo",
		loginEmail: "Prihlásenie e-mailom",
		loginIntra: "Prihlásenie cez Intra",
		loginOr: "alebo",
		firstTime: "Si tu prvýkrát?",
		createAccount: "Vytvor si účet!",
		// DASHBOARD
		modeLocal: "Miestny hráč",
		modeRemote: "Vzdialený hráč",
		modeAI: "AI hráč",
		modeTournament: "Turnaj",
		viewProfile: "Profil",
		// GAME
		hasWon: "has won!",
		buttonReplay: "Hrať znova",
		buttonMenu: "Hlavné menu",
		// TOURNAMENT
		tournamentCreate: "Vytvor turnaj",
		tournamentName: "Názov turnaja",
		tournamentNamePlaceholder: "Zadaj názov turnaja",
		tournamentSlots: "Počet hráčov",
		tournamentCreateButton: "Vytvoriť",
		tournamentJoin: "Pridaj sa k turnaju",
		tournamentJoinButton: "Pripojiť sa",
		tournamentLobby: "Herné lobby pre ",
		tournamentLobbyWait: "Čakanie na ostatných hráčov...",
		tournamentLobbyStartButton: "Začať hru",
		tournamentLobbyCancelButton: "Zrušiť lobby",
		// PROFILE
		tabProfile: "Profil",
		tabMatches: "História zápasov",
		tabFriendlist: "Zoznam priateľov",
		profileAccountName: "Názov účtu",
		profileDisplayName: "Prezývka",
		editDisplayName: "Zmena prezývky",
		editProfilePic: "Zmena profilového obrázka",
	}
};

document.addEventListener("DOMContentLoaded", () => {
	const enLink = document.getElementById("langEN");
	const czLink = document.getElementById("langCZ");
	const skLink = document.getElementById("langSK");

	enLink.addEventListener("click", (event) => {
		event.preventDefault();
		setLanguage("en");
	});

	czLink.addEventListener("click", (event) => {
		event.preventDefault();
		setLanguage("cz");
	});

	skLink.addEventListener("click", (event) => {
		event.preventDefault();
		setLanguage("sk");
	});

	// Load the preferred language from local storage or default to English
	const preferredLanguage = localStorage.getItem("language") || "en";
	setLanguage(preferredLanguage);
});

function setLanguage(language) {
	document.querySelectorAll("[data-translate]").forEach(element => {
		const key = element.getAttribute("data-translate");
		if (element.tagName === "INPUT" && element.hasAttribute("placeholder")) {
			element.setAttribute("placeholder", translations[language][key] || translations['en'][key]);
		} else {
			element.textContent = translations[language][key] || translations['en'][key];
		}
	});

	// Store the selected language in local storage
	localStorage.setItem("language", language);
}