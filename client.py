import socket
import threading

def listen_for_notifications(client_socket):
    """Listens for incoming messages from the server and prints them."""
    while True:
        try:
            response = client_socket.recv(1024).decode()  # Receive message from server
            if response:  # If there's a message, print it
                print(response)
            else:
                break  # Break if no response (server may have closed connection)
        except Exception as e:
            print("Error receiving message:", e)
            break

def connect_to_server(host='127.0.0.1', port=65432):
    """Connects to the server and handles user input for commands."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    client_socket.connect((host, port))  # Connect to the server
    
    username = input("Enter a unique username: ")  # Prompt for a unique username
    client_socket.send(username.encode())  # Send username to server

    # Start a thread to listen for notifications from the server
    threading.Thread(target=listen_for_notifications, args=(client_socket,), daemon=True).start()

    while True:
        command = input("Enter command: ")  
        
        # Check for empty command input
        if not command.strip():  # If command is empty or only whitespace
            print("Warning: Command cannot be empty. Please enter a valid command.")  # Warning message
            continue  # Skip the rest of the loop and prompt for input again
        
        if command.startswith("%connect"):
            client_socket.send(command.encode())  
            continue
        
        if command == "%exit":
            break
        
        if command == "%join":
            client_socket.send(command.encode())  
            continue
        
        client_socket.send(command.encode())  # Send valid command to server

    client_socket.close()  # Close connection when done

if __name__ == "__main__":
    connect_to_server()  # Run the client when this script is executed