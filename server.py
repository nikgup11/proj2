# pylint: disable=broad-exception-caught
import socket
import threading
from datetime import datetime

# Server configuration
HOST = '127.0.0.1'  # Localhost address
PORT = 65432        # Non-system port (for server to listen on)

clients = {}  # Keeps track of all clients on board
messages = []  # Tracks all the messages in a board
lock = threading.Lock()  # Using lock for the multi-threaded TCP's keeps data integrity since many threads are accessing shared resources like messages
groups = {  # Groups for the message board
    "Group1": {"users": [], "messages": []},
    "Group2": {"users": [], "messages": []},
    "Group3": {"users": [], "messages": []},
    "Group4": {"users": [], "messages": []},
    "Group5": {"users": [], "messages": []}
}

# Deals with client communication and all the commands they input
def handle_client(conn, addr):
    username = conn.recv(1024).decode()  # Receive the username from client

    # Register new user, notify others in the board and update user list
    with lock:
        clients[conn] = username
        notify_users(f"{username} has joined the chat.\n")
        list_groups(conn)

    # Command handling loop
    while True:
        try:
            msg = conn.recv(1024).decode()  # Wait for client command input
            if msg.startswith("%post_group"):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    conn.send("Invalid command. Usage: %post_group group_name message".encode())
                else:
                    group_name, content = parts[1], parts[2]
                    post_group_message(conn, username, content, group_name)
            elif msg.startswith("%post"):
                post_message(username, msg[6:])
            elif msg.startswith("%message "):  # Handle %message command
                message_content = msg[9:]  # Remove "%message " from the string
                post_message(username, message_content)  # Call post_message
            elif msg.startswith("%leave_group"):
                parts = msg.split()
                if len(parts) < 2:
                    conn.send("Invalid command. Usage: %leave_group group_name".encode())
                else:
                    group_name = parts[1]
                    leave_group(conn, username, group_name)
            elif msg.startswith("%leave"):
                leave(conn, username)
            elif msg.startswith("%users"):
                send_user_list(conn)
            elif msg.startswith("%messages"):
                parts = msg.split()
                if len(parts) < 2:
                    conn.send("Invalid command. Usage: %messages group_name".encode())
                else:
                    group_name = parts[1]
                    retrieve_group_messages(conn, group_name) # NEED TO IMPLEMENT THIS
            elif msg.startswith("%connect"):  # NOTE: Needs more implementation
                handle_connect(conn, msg[9:])
            elif msg.startswith("%join"):
                group_name = msg.split()[1]
                handle_join(conn, username, group_name)
            elif msg.startswith("%groups"):
                list_groups(conn)
            elif msg.startswith("%retrieve_message"):  # Handle message retrieval by ID
                parts = msg.split()
                if len(parts) < 2:
                    conn.send("Invalid command. Usage: %retrieve_message message_id".encode())
                else:
                    message_id = parts[1]
                    retrieve_message(conn, message_id)  # Retrieve the message by ID
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            break

    conn.close()

# Sends notification to all clients in board
def notify_users(message):
    for client in clients.keys():
        client.send(message.encode())

# Sends the current list of users to requesting client
def send_user_list(conn):
    # MAY NEED TO SORT SO YOU ONLY SEE USERS IN YOUR GROUP
    user_list = ", ".join(clients.values())
    conn.send(f"Current users: {user_list}".encode())

# Posts a new message
def post_message(sender, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time
    message_id = len(messages) + 1  # Generate new message ID
    message = f"{message_id}, {sender}, {timestamp}, {content}"  # Format the message
    
    with lock:
        messages.append(message)  # Add the new message to the list
        if len(messages) > 2:  # Keep only the last 2 messages
            messages.pop(0)

    # Notify all users
    notify_users(message)

# Retrieves and sends message by ID to the requesting client
def retrieve_message(conn, message_id):
    try:
        message_id = int(message_id)  # Convert ID to integer
        # Retrieve the message from the list
        if 1 <= message_id <= len(messages):
            message = messages[message_id - 1]  # Get the message
            conn.send(f"Message {message_id}: {message}".encode())  # Send the message to the client
        else:
            conn.send(f"Error: Message ID {message_id} not found.".encode())
    except ValueError:
        conn.send("Invalid message ID.".encode())  # Handle invalid ID

# Current client leaves bulletin board chat
def leave_group(conn, username, group_name):
    with lock:
        # Check if the group exists
        if group_name not in groups:
            conn.send(f"Error: Group '{group_name}' does not exist.".encode())
            return

        # Check if the user is in the group
        if conn not in groups[group_name]["users"]:
            conn.send(f"Error: You are not a member of '{group_name}'.".encode())
            return

        # Remove the user from the group
        groups[group_name]["users"].remove(conn)
        print(f"{username} has left {group_name}.")

        # Notify other members of the group
        notify_group_users(group_name, f"{username} has left {group_name}.")

        # Send confirmation to the user
        conn.send(f"You have left the group '{group_name}'.".encode())


# Connect to server by specific address and port
def handle_connect(conn, address_port):
    conn.send(f"Attempting to connect to {address_port}...".encode())

# Join msg board 
def handle_join(conn, username, group_name):
    try:
        # Step 1: Check if the group exists (no need to hold the lock here)
        if group_name not in groups:
            conn.send(f"Error: Group '{group_name}' does not exist.".encode())
            return

        # Step 2: Check if the user is already in the group (lock for modification)
        with lock:
            if conn in groups[group_name]["users"]:
                conn.send(f"You are already a member of '{group_name}'.".encode())
                return

            # Step 3: Append the user to the group's user list
            print(f"Appending {username} to group {group_name}.")
            groups[group_name]["users"].append(conn)
            print(f"Group {group_name} now has members: {groups[group_name]['users']}")

            # Step 4: Notify group members
            notify_group_users(group_name, f"{username} has joined {group_name}.")
            conn.send(f"Joined group '{group_name}'.".encode())

    except Exception as e:
        print(f"Error handling join for {username} in {group_name}: {e}")
        conn.send(f"An error occurred while joining the group: {e}".encode())

# Starts server and listen for new connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket object
    server_socket.bind((HOST, PORT))  # Bind to host and port
    server_socket.listen()  # Start the listener
    
    print("Server started. Waiting for connections...")
    
    while True:
        conn, addr = server_socket.accept()  # Accept new client connections
        print(f"Connection from {addr}") 
        threading.Thread(target=handle_client, args=(conn, addr)).start()  # Start a new thread for each client

def notify_group_users(group_name, message):
    for client in groups[group_name]["users"]:
        try:
            # Check if the client socket is still open and can send a message
            client.send(message.encode())  # Attempt to send the message
        except (BrokenPipeError, ConnectionResetError) as e:
            # Handle specific socket errors (disconnection)
            print(f"Error sending message to {client}. Client may be disconnected. Error: {e}")
            try:
                # Try to safely remove the disconnected client
                groups[group_name]["users"].remove(client)
                print(f"Removed {client} from group {group_name} due to disconnection.")
            except ValueError:
                # Handle case where the client might not be in the group list
                print(f"Client {client} was not in the group list when trying to remove.")
        except Exception as e:
            # Catch other unexpected exceptions
            print(f"Unexpected error when notifying {client}. Error: {e}")

def post_group_message(conn, sender, content, group_name):
    with lock:
        # Check if the group exists
        if group_name not in groups:
            conn.send(f"Error: Group '{group_name}' does not exist.".encode())
            return

        # Check if the user is a member of the group
        if conn not in groups[group_name]["users"]:
            conn.send(f"Error: You are not a member of '{group_name}'.".encode())
            return

        # Post the message to the group
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_id = len(groups[group_name]["messages"]) + 1
        message = f"{message_id}, {sender}, {timestamp}, {content}"
        groups[group_name]["messages"].append(message)

        # Notify all group members
        notify_group_users(group_name, f"Group message from {sender}: {content}")

# List all groups available to the client
def list_groups(conn):
    group_list = ", ".join(groups.keys())
    conn.send(f"Available groups: {group_list}".encode())

def leave(conn, username):
    with lock:
        for group in groups.values():
            if conn in group["users"]:
                group["users"].remove(conn)
                print(f"{username} has left {group}.")
                notify_group_users(group, f"{username} has left the chat.")
        if conn in clients:
            del clients[conn]
            notify_users(f"{username} has left the chat.")
            conn.send("You have left the chat.".encode())
        else:
            conn.send("You are not connected to the chat.".encode())

# This block ensures that the server runs when the script is executed directly
if __name__ == "__main__":
    start_server()
