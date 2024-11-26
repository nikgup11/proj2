import socket
import threading
from datetime import datetime

# Server configuration
HOST = '127.0.0.1'  # Localhost address
PORT = 65432        # Non-system port (for server to listen on)

clients = {} # Keeps track of all clients on board
messages = [] # Tracks all the messages in a board
lock = threading.Lock() # Using lock for the multi-threaded TCP's keeps data integrity since many threads are accessing shared resources like messages

# Deals with client communication and all the commands they input
def handle_client(conn, addr):
    username = conn.recv(1024).decode() # Receive the username from client
    
    # Register new user, notify others in the board and update user list
    with lock:
        clients[conn] = username 
        notify_users(f"{username} has joined the chat.")
    # Command handling
    while True:
        try:
            msg = conn.recv(1024).decode() # Wait for client cmd input 
            if msg.startswith("%post"):
                post_message(username, msg[6:])
            elif msg.startswith("%leave"):
                leave_chat(conn, username)
                break
            elif msg.startswith("%users"):
                send_user_list(conn)
            elif msg.startswith("%message"):
                retrieve_message(msg[9:], conn)
            elif msg.startswith("%connect"): # NOTE: Probably needs more implemented to it
                handle_connect(conn, msg[9:])
            elif msg.startswith("%join"): # NOTE: Probably needs more implemented to it
                handle_join(conn, username)
        except:
            break

    conn.close()

# Sends notification to all clients in board
def notify_users(message):
    for client in clients.keys():
        client.send(message.encode())

# Sends the current list of users to requesting client
def send_user_list(conn):
    user_list = ", ".join(clients.values())
    conn.send(f"Current users: {user_list}".encode())

# Posts a new message
def post_message(sender, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Current time
    message_id = len(messages) + 1 # Generate new message id
    message = f"{message_id}, {sender}, {timestamp}, {content}" # Message format
    
    with lock:
        messages.append(message) # Add new message to list
        if len(messages) > 2: # Keep only the last 2 messages
            messages.pop(0)  
    
    notify_users(message)

# Retrieves and sends message by ID to the requesting client
def retrieve_message(message_id, conn):
    try:
        message_id = int(message_id)
        message = messages[message_id - 1]
        conn.send(f"Message {message_id}: {message}".encode())
    except (IndexError, ValueError):
        conn.send("Invalid message ID.".encode())

# Current client leaves bulletin board chat
def leave_chat(conn, username):
    with lock:
        del clients[conn]
        notify_users(f"{username} has left the chat.")

# Connect to server by specific address and port
def handle_connect(conn, address_port):
    conn.send(f"Attempting to connect to {address_port}...".encode())

# Join msg board 
def handle_join(conn, username):
    conn.send(f"{username} has joined the public message board.".encode())

# Starts server and listen for new connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket object
    server_socket.bind((HOST, PORT)) # Bind to host and port
    server_socket.listen() # Start the listener
    
    print("Server started. Waiting for connections...")
    
    while True:
        conn, addr = server_socket.accept() # Accept new client connections
        print(f"Connection from {addr}") 
        threading.Thread(target=handle_client, args=(conn, addr)).start() # Start a new thread for each client

if __name__ == "__main__":
    start_server()