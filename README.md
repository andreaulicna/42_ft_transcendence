<div align="center">
  <img src="nginx/assets/praguescendence_logo.png" alt="Praguescendence Logo">
</div>

## Project description
ft_transcendence is the final project of the [42 Common Core](https://www.42prague.com/studies). The goal is to build a full-stack single page application where users can play Pong. The version you're seeing now, 42_praguescendence, was made by 42 Prague students aulicna, plouda and vbartos.

The subject outlines a mandatory part, the tech stack, and multiple additional modules which complement the mandatory base part. Based on the subject's constraints, the tech stack consists of Vanilla JavaScript and Bootstrap for the front-end, Python Django for the back-end, and PostgreSQL for the database.

Notable features include
- Pong game running server-side;
- local (same keyboard) and remote (connected from different devices) modes;
- 2FA;
- JWT authentication;
- OAuth;
- user management (uploading profile pictures, match history, friendships, etc.);
- adaptive AI opponent;
- mobile device responsibility.

## Prerequisites to run the project
`cert.pem` and `key.pem` in `nginx/certs/`
<br>
`.env` in root directory
```
POSTGRES_PASSWORD=
INTRA_APP_UID=
INTRA_APP_SECRET=
WWW_DOMAIN= # change to current PC IP + change callback URI in intra
SECRET_KEY=''
```

## Running the project
- download repo;
- setup the prerequisites (.env file, SSL certs);
- startup Docker;
- build the project via the Makefile with `make build`;
- connect to the app via `https://localhost:4200/`