# Server Protocol

## SSL encryption
First of all: You have to use an **SSL encrypted** connection with a valid certificate.

## Server output
To communicate the server uses the **pickle** library. Every data object sent to the client
is a dictionary containing at least the `key` and `action` attributes.

The `key` attribute gives the generic topic, e.g. _chat_, _server_, _tournament_, etc.
The `action` attribute gives more specific info, e.g. _joined_, _left_, _new_, etc.
Every specific data object sent to the client can contain more attributes that are described
in the following.

## Server structure
The server is separated in multiple rooms, called `server`. Some of them are game servers,
some other servers are only chat rooms.

The server with id `0` is the hub. Here you can switch between the different servers. Since being
a lobby server, you can use the chat feature to communicate with the other players. Additionally you
can join the game queue or handle tournaments.

## Commands and server output


### Login system
**key**: `login`

#### Username / password
**action**: `username` / `password`
When the given query is sent by the server, the client has to return a valid username and password.
**Important**: You may not send anything else in the meantime!

#### Invalid attempts
**action**: `invalid`
This is sent when the username or password are invalid.

#### Connected
**action**: `connected`
This is sent when the login attempt was confirmed successfully.


### Server specific
**key**: `server`

#### Player status
**action**: `players`
Returns the current players being on the server, whenever somebody joins or leaves the server.

##### Arguments
**players**: List of players

#### Moved to other server
**action**: `moved`
Returns the current server whenever the server is changed.

##### Arguments
**to**: Server id of new server
**state**: State of this server, e.g. `default`, `playing`, etc.

#### Join / leave other servers
Use `join <id> [args]` to join the server specified by `id`.
To join a game server as a player, you have to append `player` as extra argument.

Use `leave` to return to the hub.

#### Available game servers
**action**: `active`
Is returned as an answer to the query `games`.

##### Arguments
**servers**: List of active game servers.


### Game
**key**: `game`

#### Started / Finished
**action**: `started` / `finished`
Is sent when a game starts or finishes.

#### Initial setup / Updates
**action**: `init`, `update`
Is sent in the beginning of a match (`init`) or after every turn (`update`).

#### Start the game
You can send your AI file with `ai <ai-code>`. You must have sent the AI code before you can use
`start` to tell the server that the player is ready. As soon as every player has sent `start` to
the server, the game is started.


### Chat
**key**: `chat`

#### Receive new message
**action**: `new`
Is sent whenever there is a new message for the user

##### Arguments
**mode**: `global` or `private`
**text**: the message body
**from**: the sender

#### Send messages
Send `chat <recipient> <text>` to the server to send a message.
The recipient is `global` or an online player.


### Queue
**key**: `queue`

#### Join / Leave
Send `join queue` to join the queue and `leave queue` to leave the queue.

Respectively the actions `joined` or `left` are sent back.


### Tournaments
**key**: `tournament`

#### Info
Send `tournament info` to get information about the current tournaments.

This returns the action `info` and several tournament attributes.

#### Join / Leave
Send `tournament join <ai-code>` to join the tournament and `tournament leave` to leave the tournament.

#### Create / Remove
As an admin you can use `tournament create <name>` and `tournament remove` to create / remove the
tournament.

This returns the actions `created` / `removed`.
