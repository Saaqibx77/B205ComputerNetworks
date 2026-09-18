#client.py
import socket
import json
import threading


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

BUFFER_SIZE = 4096



# CONNECTING WITH SERVER


client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)



# SENDING THE REQUEST FOR COMMUNICATION


def send_request(data):

    message = json.dumps(data) + "\n"

    client.sendall(
        message.encode("utf-8")
    )



# RECEIVE SERVER DATA

def receive_messages():

    while True:

        try:

            data = client.recv(BUFFER_SIZE)

            if not data:

                print("\nServer disconnected.")

                break

            messages = data.decode("utf-8").splitlines()

            for message in messages:

                if message.strip():

                    response = json.loads(message)

                    process_response(response)

        except Exception as error:

            print("\nReceive error:",error)
            

            break



# PROCESS RESPONSE


def process_response(response):

    response_type = response.get("type")
    if response_type == "message":
        print("\n--------------------------------")

        print("NEW MESSAGE FROM "
            f"{response['sender']}:")

        print(response["message"])

        print("--------------------------------")


    elif response_type == "online_users":

        print("\nOnline users:",response["users"])


    elif response_type == "history":

        print("\n========== CHAT HISTORY ==========")

        for message in response["messages"]:

            print(f"{message['timestamp']} | "
                f"{message['sender']} -> "
                f"{message['receiver']} | "
                f"{message['message']}")

        print("=================================")


    else:

        print("\nSERVER:", response)



# REGISTERATION PROCESS


def register():

    username = input("Enter username: ")

    password = input("Enter password: ")

    send_request({"type": "register",
            "username": username,
            "password": password})



# LOGIN


def login():

    username = input("Username: ")

    password = input("Password: ")

    send_request({"type": "login","username": username,"password": password} )



# SEND MESSAGE


def send_message():

    receiver = input("Receiver username: ")

    message = input("Enter message: ")

    send_request({
            "type": "message",
            "receiver": receiver,
            "message": message
        })



# ADD CONTACT


def add_contact():

    contact = input("Enter contact username: ")

    send_request({
            "type": "add_contact",
            "contact": contact
        })



# SHOW CONTACTS


def show_contacts():

    send_request({
            "type": "get_contacts" })



# CHAT HISTORY


def chat_history():

    user = input("Enter username: ")

    send_request({
            "type": "history",
            "user": user
        })



# MAIN MENU


def main_menu():

    while True:

        print("\n")
        print("=" * 40)
        print("       MESSAGING APPLICATION")
        print("=" * 40)

        print("1. Send Message")
        print("2. Add Contact")
        print("3. Show Contacts")
        print("4. Chat History")
        print("5. Logout")

        choice = input("Enter choice: ")


        if choice == "1":

            send_message()


        elif choice == "2":

            add_contact()


        elif choice == "3":

            show_contacts()


        elif choice == "4":

            chat_history()


        elif choice == "5":

            print("Logging out...")

            break


        else:

            print("Invalid choice.")



# MAIN


def main():

    try:

        client.connect((
                SERVER_IP,
                SERVER_PORT
            ) )

        print("\nConnected to messaging server!")


        receiver_thread = threading.Thread(target=receive_messages,daemon=True)

        receiver_thread.start()


        while True:

            print("\n")
            print("1. Register")
            print("2. Login")
            print("3. Exit")

            choice = input("Enter choice: ")


            if choice == "1":

                register()


            elif choice == "2":

                login()

                main_menu()

                break


            elif choice == "3":

                client.close()

                break


            else:

                print(
                    "Invalid choice."
                )


    except ConnectionRefusedError:

        print("\nERROR: Server is not running.")

        print("Start server.py first.")


    except Exception as error:

        print("\nERROR: ",error")


if __name__ == "__main__":

    main()
