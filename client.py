import socket
import threading

def listen_for_notifications(client_socket):
    """Handles incoming notifications from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode()  # Receive message from server
            if message:
                print(message)  # Print the received message (e.g., notifications, messages)
        except Exception as e:
            print(f"Error listening for notifications: {e}")
            break

def connect_to_server(host='127.0.0.1', port=65432):
    """Connects to the server and handles user input for commands."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))  # Connect to the server
    
    # Prompt for a unique username and send it to the server
    username = input("Enter a unique username: ")
    client_socket.send(username.encode())  # Send username to server

    # Start a thread to listen for notifications from the server
    threading.Thread(target=listen_for_notifications, args=(client_socket,), daemon=True).start()

    while True:
        command = input()

        # Check for empty command input
        if not command.strip():  # If command is empty or only whitespace
            print("Warning: Command cannot be empty. Please enter a valid command.")  # Warning message
            continue  # Skip the rest of the loop and prompt for input again
        
        if command.startswith("%connect"):
            # If the command is %connect, parse out the host and port
            try:
                _, new_host, new_port = command.split()  # Expecting %connect <host> <port>
                new_port = int(new_port)  # Convert port to integer

                # Disconnect from the current server
                client_socket.close()

                # Connect to the new server specified by the command
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((new_host, new_port))  # Connect to new host/port
                print(f"Connected to {new_host}:{new_port}")

                # Send the username again after reconnecting
                client_socket.send(username.encode())

                # Start listening for notifications again
                threading.Thread(target=listen_for_notifications, args=(client_socket,), daemon=True).start()
            
            except ValueError:
                print("Error: %connect command requires a host and port (e.g., %connect 127.0.0.1 65432).")
            continue
        
        if command == "%exit":
            client_socket.send(command.encode())  # Send %exit command to server
            break
        
        # Send valid commands to the server
        client_socket.send(command.encode())  

    client_socket.close()  # Close connection when done


if __name__ == "__main__":
    connect_to_server()  # Run the client when this script is executed