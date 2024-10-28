## API endpoints
### Notes
1. `5xx` status codes usually mean something in backend has gone wrong, be prepared to intercept those for any call made to API

2. If a response contains any details with regard to why it was sent (e.g. `404` when a user is not found), it is encoded in the key-value pair: `{"detail" : "reason" }`

3. `401` is raised on any API call that doesn't have a valid `Bearer` token if the endpoint requires authentication, `405` on any API call whose method is not supported (e.g. a POST request on endpoint that only supports GET requests)
### `/api/user`

| Endpoint | Supported methods | Required input | Return codes | Authentication required |
| :--- |---|:---| :---:| :---: |
| `/register` |POST|`username`<br>`password`<br>`email`| 201<br>400 | &cross; |
| `/info` |GET, PUT|  `last_name` (PUT)<br> `first_name` (PUT)| 200<br>404 | &check; |
| `/avatar` | GET, (PUT) | JSON-encoded image | 200 (GET)<br>201 (PUT)<br>404 | &check; |
| `/match` | GET, POST<sup>1</sup> |  | 200 (GET)<br>201 (POST)<br>400<br>404 | &check; |
| `/users-list`<sup>2</sup> | GET|  | 200  | &check; |
| `/friendships`<sup>3</sup> | GET, POST |  | 200<br>201 (POST)<br>400<br>404 | &check; |

<sup>1</sup> Pairs two random players together and creates a match, will change over time<br>
<sup>2</sup> Only available for debugging purposes for now, will net slightly different results for authenticated and non-authenticated users in the future<br>
<sup>3</sup> Sends a friend request to a random existing user that is not identical to the sender, will change over time, no accept/refuse functionality yet<br><br><br>


### `/api/auth`
| Endpoint | Supported methods | Required input | Return codes | Authentication required |
| :--- |---|:---| :---:| :---: |
| `/token` |POST|`username`<br>`password`<br>| 200<br>401 | &cross; |
| `/token/refresh` |POST|| 200<br>401 | &check; |
| `/ws-login` |GET|| 200<br>401 | &check; |
|`/ws/init/`<br>(mind the slash at the end) |non-HTTP|`?uuid=`|Connected<br>Disconnected|?|


- `/token` returns both `access` and `refresh` tokens - `access` currently lasts for an hour, `refresh` for 24 hours<br>
- `/token/refresh` only returns a new `access` token
- flow for websocket connection:
	1. login as an existing user
	2. send a request to `/ws-login` with the JWT token
	3. save the returned `uuid`
	4. send the WEBSOCKET request to `/ws/init/?uuid=returneduuidnumber`
	5. profit

