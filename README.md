# Project 2 - Nikhil Gupta & Eli Pappas
**Compile and Run Instructions:**
* Open a terminal into the directory of the server.py file
* Enter "python server.py" to start the server
* Open another terminal into same directory where the client.py file should be located
* Enter "python client.py" to start a new client

**Usability Instructions:**
* %retrieve_message - command followed by message ID to retrieve the content of the message (part 1)
* %group_join - command followed by the group id/name to join a specific group
* %group_messages - command followed by the group id/name and message ID to retrieve the content of the message posted earlier on a message board owned by a specific group
* %group_leave -  command followed by the group id/name to leave a specific group.
* %group_post - command followed by the group id/name, the message subject, and the message content or main body to post a message to a message board owned by a specific group.
* %leave - command which allows you to leave all chats (groups, public) at once.
* %join - command which allows you to rejoin the chat after leaving. This is automatically run for you on launch.
* %users - displays all active users in the public chat.
* %groups - displays all groups
* %post - command followed by message which gets posted to the public chat.
* %exit - terminates all connections and disconnects you from the server.
* %group_users - lists all users in any group specified.


**NOTABLE DOCUMENTATION:**
* With regards to the %connect command, while it is implemented and operational, it returns an error when called because when starting client.py, it automatically connects to the server since there is only one server connect to which we hard code into the server.py. Therefore, the error happens because we try to connect when a connection is already established. That being said, the code is still operational even when the connection issue occurs, all that happens is that the server disconnects and re-connects, and an error message appears in the server terminal window. More details and reasoning as to why this is part of the code is given in the Major Issues & Fixes below. 

**Major Issues & Fixes:**
The two biggest issues faced were %connect and %exit. When exiting a group or the chat, an exception would be caught that had to do with bad file directory, which we couldn't explain why that was the issue. However, after some de-bugging we fixed it by checking that the client socket was closed when the %exit command goes to the notification listener in client.py, and breaking out of the listener and the client. The %connect command was more of a higher-level issue, which is because our implementation automatically connected to the server when running client.py, so when you try to connect to the same 127.0.0.1:65432 server/port from within the server itself, it disconnects and reconnects fine, but an error is thrown. The issue was just deciding whether we wanted to leave the implementation as is or adjust how the user is prompted. This is just a quirk of our implementation since we automatically connect anyways and this could be fixed by simply prompting for the %connect sommand before asking for username input or allowing for chat commands, but since we are using only one server, this would be redundant so we've left it the way it is.    
