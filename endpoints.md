## API endpoints
### Changelog
31/10/24 <br/>
Deleted `/api/user/friendships`, reworked `/api/user/friends` endpoint, updated friend functionality

### Notes
1. Authentication is required for all endpoints except `/api/user/register` and `/api/auth/token`

2. `5xx` status codes usually mean something in backend has gone wrong, be prepared to intercept those for any call made to API

3. If a response contains any details with regard to why it was sent (e.g. `404` when a user is not found), it is encoded in the key-value pair: `{"detail" : "reason" }`

4. `401` is raised on any API call that doesn't have a valid `Bearer` token if the endpoint requires authentication, `405` on any API call whose method is not supported (e.g. a POST request on endpoint that only supports GET requests)
### `/api/user`

| Endpoint | Supported methods | Required input | Return codes | Notes |
| :--- |---|:---| :---:| :---: |
| `/register` |POST|`username`<br>`password`<br>`email`| 201<br>400 |  |
| `/info` |GET, PUT|  `last_name` (PUT)<br> `first_name` (PUT)<br> `username` (PUT)| 200<br>404 | Current user info |
| `<int:pk>/info` |GET| | 200<br>404 | User info based on the provided user_id |
| `/avatar` | GET, (PUT) | JSON-encoded image | 200 (GET)<br>201 (PUT)<br>404 | currently non-functional |
| `/match` | GET |  | 200 (GET)<br>400<br>404 | shows history of all matches for a specific user |
| `/users-list`<sup>2</sup> | GET|  | 200  | &check; |
| `/friends`<br>`/friends/sent`<br>`/friends/received` | GET |  | 200 | lists accepted requests (aka. friendships), sent friend requests and received friend requests respectively |
| `/friends/request/<str:username>` | POST |  | 201, 400, 404 | e.g. `/friends/requests/testusr1` sends a friend request to `testusr1`|
| `/friends/<int:pk>/accept`<br>`/friends/<int:pk>/refuse`<br>| POST| | 200, 404| only related to pending friend requests, it should treat irrelevant or already accepted requests as "Not found" |
| `/friends/<int:pk>/delete`| DELETE || 200, 404| deletes an active friendship OR, if the user is the sender, a pending friend request (basically withdraws the request) |
| `/match-history`| GET || 200, 404| lists all matches a user played, specifying `type` variable to distinguish between them |
| `/win-loss`| GET || 200, 404| returns overall, remote match and AI match win-loss counts |
| `/users-status`| GET || 200, 404| returns a list of user with their id, username and status (`ON` or `OFF`) based on `status_counter` saved in user object |
| `/debug/info/reset`| POST | | 200, 404 | Resets user state from any to OFF 

<sup>2</sup> Only available for debugging purposes for now, will net slightly different results for authenticated and non-authenticated users in the future<br>


### `/api/auth`
| Endpoint | Supported methods | Required input | Return codes | Notes |
| :--- |---|:---| :---:| :---: |
| `/login` |POST|`username`<br>`password`<br> | 200<br>401 | Sets `refresh_token` cookie, returns `access` token in body, sets `csrftoken` cookie|
| `/login/refresh` |POST|| 200<br>400<br>401 | Refreshes `access` token and issues a new `refresh_token` |
|`login/refresh/logout`| POST | | 200<br>401 | Blacklists `refresh_token` and expires the relevant cookie |
| `/ws-login` |GET|| 200<br>401 | Returns short-lived `uuid` for websocket use |


- `/token` returns both `access` and `refresh` tokens - `access` currently lasts for an hour, `refresh` for 24 hours<br>
- `/token/refresh` only returns a new `access` token
- flow for websocket connection:
	1. login as an existing user
	2. send a request to `/ws-login` with the JWT token
	3. save the returned `uuid`
	4. send the WEBSOCKET request to `api/ws/auth/init/?uuid=returneduuidnumber`
	5. profit

### `/api/localplay`
| Endpoint | Supported methods | Required input | Return codes | Notes |
| :--- |---|:---| :---:| :---: |
| `/match`|POST|`player1_tmp_username`<br>`player2_tmp_username`|201<br>400|Creates a local match in the database and returns its id
| `/<int>prev_match_id>/rematch/<str:sides_mode>`|POST|-|201<br>400<br>404|Creates rematch of a local match in the database and returns its id.<br> `sides_mode` should be "switch" for a rematch when players want to switch sides and "keep" otherwise.

### `/api/ai`
| Endpoint | Supported methods | Required input | Return codes | Notes |
| :--- |---|:---| :---:| :---: |
| `/match`|POST||201<br>400|Creates an AI match in the database and returns its id


### `/api/tournament`
| Endpoint | Supported methods | Required input | Return codes | Return values | Notes |
| :--- |---|:---| :---:| :---: | :---: |
|`/create/<cap:capacity>/`|POST|`tournament_name`(optional)<br>`player_tmp_username`(optional)|201<br>400<br>403<br>404|`tournament` object with all info from the database |Creates a tournament and player_tournament database entries.
|`/local/create/<cap:capacity>/`|POST|`players = ["usr1", "usr2', "usr3", "usr4"]`<br>`tournament_name`(optional)|201<br>400<br>403<br>404|`local_tournament` object with all info from the database |Creates a local tournament database entries.
|`/join/<int:tournament_id>/`|POST|`player_tmp_username`(optional)|201<br>400<br>403<br>404|`tournament` object with all info from the database, including a list of `players` in the tournament |Adds `player` into a tournament based on `tournamend_id` in URL.
|`/join/cancel/<int:tournament_id>/`|POST||200<br>403<br>404|`tournament` object with all info from the database, including a list of `players` in the tournament|Deletes a user from waiting tournament based on `tournament_id` in URL.
|`/list/waiting` | GET ||200<br>404|list object of all waiting tournaments, including free spaces for players to join ||
|`/list/player` | GET || 200<br>404| list object of all tournaments for a particular user ||
|`/info/<int:tournament_id>/` | GET || 200<br>404| tournament object |provides tournament info based on the id in url, including the list of players |

### `/api/ws`
| Endpoint | Supported methods | Required input | Return codes | Notes |
| :--- |:---:|:---| :---:| :--- |
|`/auth/init/` |non-HTTP|`?uuid=`|Connected<br>Disconnected| Changes user status to ON on connect, and to OFF on disconnect |
|`/pong/<int:match_id>/`|non-HTTP|`?uuid=`|Connected<br>Disconnected|Waits for players to join & starts the remote match
|`/matchmaking/`|non-HTTP|`?uuid=`|Connected<br>Disconnected|Pairs players and return their match_id
|`/localplay/<int:match_id>/`|non-HTTP|`?uuid=`|Connected<br>Disconnected|Waits for players to join & starts the local match
|`/ai/<int:match_id>/`|non-HTTP|`?uuid=`|Connected<br>Disconnected|Waits for players to join & starts the ai match
|`/tournament/<int:tournament_id>/`|non-HTTP|`?uuid=`|Connected<br>Disconnected|Matchmaking for tournament. Returns `match_id` (that is to be used to connect to `/pong/<int:match_id>/`) if there is a match to play for the particular `player`.
|`/tournament/local/<int:tournament_id>/`|non-HTTP|`?uuid=`|Connected<br>Disconnected|Matchmaking for local tournament. Returns `match_id` (that is to be used to connect to `/localplay/<int:match_id>/`) if there is a local match to play in the particular tournament.