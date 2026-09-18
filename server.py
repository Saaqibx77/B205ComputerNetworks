#server.py
import socket
import threading
import json
import os
import logging

from database import (initialize_database,
    register_user,authenticate_user,
    add_contact,get_contacts,save_message,
    get_messages) #import all required functions


# CONFIGURATION


HOST = "127.0.0.1"
PORT = 5000

BUFFER_SIZE = 4096
MAX_FILE_SIZE = 10 * 1024 * 1024 #control max size for now 10mb



# CONNECTED CLIENTS


clients = {}

clients_lock = threading.Lock()



# LOGGING


os.makedirs("logs", exist_ok=True) #create directory to store all logs info

logging.basicConfig(filename="logs/server.log",level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")



# SEND JSON


def send_json(client_socket, data):

    message = json.dumps(data) + "\n"

    client_socket.sendall(message.encode("utf-8"))



# BROADCAST ONLINE USERS


def broadcast_status():

    with clients_lock:

        online_users = list(clients.keys())

        for username, sock in clients.items():

            try:

                send_json(sock,{"type": "online_users",
                        "users": online_users
                    })

            except Exception as error:

                logging.error(str(error))



# SEND MESSAGE TO USER


def send_to_user(username, data):

    with clients_lock:

        sock = clients.get(username)

        if sock:

            try:

                send_json(sock, data)

                return True

            except Exception as error:

                logging.error(str(error))

    return False



# CLIENT HANDLER


def handle_client(client_socket, client_address):

    username = None

    print(f"\n[+] Client connected: {client_address}")

    logging.info(f"Client connected: {client_address}")

    try:

        while True:

            data = client_socket.recv(BUFFER_SIZE)

            if not data:

                break

            try:

                request = json.loads(data.decode("utf-8").strip())

            except json.JSONDecodeError:

                send_json(client_socket,{
                        "type": "error",
                        "message": "Invalid JSON"})

                continue

            request_type = request.get("type")


            
            # REGISTER
            

            if request_type == "register":

                user = request.get("username")
                password = request.get("password")

                success, message = register_user(user,password)

                send_json(client_socket,{
                        "type": "register_response",
                        "success": success,
                        "message": message})


            
            # LOGIN
            

            elif request_type == "login":

                user = request.get("username")
                password = request.get("password")

                if authenticate_user(user,password):

                    username = user

                    with clients_lock:

                        clients[username] = client_socket

                    print(f"[+] {username} logged in")

                    logging.info(f"{username} logged in")

                    send_json(client_socket,
                        {
                            "type": "login_response",
                            "success": True,
                            "message": "Login successful"
                        })

                    broadcast_status()

                else:

                    send_json(
                        client_socket,
                        {
                            "type": "login_response",
                            "success": False,
                            "message": "Invalid username or password"
                        })


            
            # ADD CONTACT
            

            elif request_type == "add_contact":

                contact = request.get("contact")

                success, message = add_contact(
                    username,
                    contact
                )

                send_json(client_socket,
                    {
                        "type": "contact_response",
                        "success": success,
                        "message": message
                    })


            
            # GET CONTACTS
            

            elif request_type == "get_contacts":

                contacts = get_contacts(username)

                send_json(client_socket,{
                        "type": "contacts",
                        "contacts": contacts
                    })


            
            # SEND TEXT MESSAGE
            

            elif request_type == "message":

                receiver = request.get("receiver")
                message = request.get("message")

                save_message(
                    username,
                    receiver,
                    message
                )

                delivered = send_to_user(
                    receiver,
                    {
                        "type": "message",
                        "sender": username,
                        "receiver": receiver,
                        "message": message
                    })

                send_json(
                    client_socket,
                    {
                        "type": "message_status",
                        "success": True,
                        "delivered": delivered
                    }
                )


            
            # CHAT HISTORY
            

            elif request_type == "history":

                other_user = request.get("user")

                messages = get_messages(username,other_user)

                send_json(
                    client_socket,
                    {
                        "type": "history",
                        "messages": messages
                    }
                )


            
            # FOR UNKNOWN COMMAND
            

            else:

                send_json(client_socket,
                    {
                        "type": "error",
                        "message": "Unknown command"
                    })


    except ConnectionResetError:

        print("[-] Connection reset: ",client_address)

    except Exception as error:

        logging.error("Client error:",error)
        

    finally:

        if username:

            with clients_lock:

                if username in clients:

                    del clients[username]

            broadcast_status()

            logging.info(f"{username} disconnected")

        client_socket.close()



# START SERVER


def start_server():

    initialize_database()

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(
        (HOST, PORT)
    )

    server.listen(10)

    print("="*55) #for 55 =
    print("      PYTHON CLIENT-SERVER MESSAGING")
    print("="*55) #for 55 = design purpose
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for clients...")
    print("="*55)#for 55 = design purpose

    while True:

        client_socket, client_address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address),
            daemon=True
        )

        thread.start()



# MAIN


if __name__ == "__main__":

    start_server()
