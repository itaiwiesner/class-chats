from encryption import encrypt_password
from protocol import *
from diffie_hellman import *
import socket
import select
import sqlite3

# DATA CONTAINERS
client_sockets = []  # list of all sockets connected to the server at the momment
logged_users = {}  # key-client_socket, value-username
data_to_send = {}  # key-client_socket, value-list of messages to the socket
sockets_in_rooms = {}  # key-room_name, value-list of clients sockets
socket_to_key = {}  # key-client_socket: value-encryption key

BUFFER_SIZE = 1024
USER_DB_PATH = 'database.db'
PORT = 9999


def setup_database():
    """ setup userss database """
    connection = sqlite3.connect(USER_DB_PATH)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, pswd TEXT)''')

    connection.commit()
    cursor.close()
    connection.close()


def setup_socket(ip):
    """ creates new server socket and returns it """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, PORT))
    server_socket.listen()
    return server_socket


def handle_disconected_client(current_socket):
    """ called after a client crashed. removes it from the datastractures """
    print(f'{current_socket.getpeername()} has disconnected')
    client_sockets.remove(current_socket)
    del data_to_send[current_socket]
    del socket_to_key[current_socket]

    # log out disconnected client
    if current_socket in logged_users:
        user_disconnected = logged_users[current_socket]
        del logged_users[current_socket]

        for room, sockets in sockets_in_rooms.items():
            if current_socket in sockets:
                # remove disconnected client from the room it's in
                sockets_in_rooms[room].remove(current_socket)

                # notify the other room members that the user has disconnected
                for sock in sockets_in_rooms[room]:
                    data_to_send[sock].append(build_msg(cmd='clientleft', params=[user_disconnected], key=socket_to_key[sock]))


def handle_new_connection(current_socket):
    """ handles a new client connecting to the server """
    (client_socket, client_address) = current_socket.accept()
                
    handle_key_exchange(client_socket)
    
    print(f"New client joined! {client_address}")
    client_sockets.append(client_socket)
    data_to_send[client_socket] = []
    
    
def handle_key_exchange(client_socket):
    """
    exchange keys using diffie hellman with a new client connected
    using constant prime and generator to speed the procces
    """
    secret = gen_secret()
    public = get_public(secret)
    
    client_socket.send(str(public).encode()) # send public
    client_public = int(client_socket.recv(BUFFER_SIZE).decode()) # recieve client public
        
    key = get_key(other_public=client_public, secret=secret)
    socket_to_key[client_socket] = key
    print(key)
    
    


def handle_login(current_socket, username, password):
    # encrypt password
    password = encrypt_password(password)

    connection = sqlite3.connect(USER_DB_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    username_exist = cursor.fetchone()

    cursor.execute("SELECT * FROM users WHERE username = ? AND pswd = ?", (username, password))
    password_match = cursor.fetchone()

    cursor.close()
    connection.close()

    # check if username exists
    if not username_exist:
        cmd, params = "error", ["username doesn't exist"]

    # check if password match
    elif not password_match:
        cmd, params = "error", ["wrong password"]

    # check if user is already logged in
    elif username in logged_users.values():
        cmd, params = 'error', ["user already logged in"]

    else:
        logged_users[current_socket] = username
        cmd, params = 'success', []

    data_to_send[current_socket].append(build_msg(cmd=cmd, params=params, key=socket_to_key[current_socket]))


def handle_signup(current_socket, username, password):
    # encrypt password
    password = encrypt_password(password)

    connection = sqlite3.connect(USER_DB_PATH)
    cursor = connection.cursor()

    # check if username exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    username_exists = cursor.fetchone()
    if username_exists:
        cmd, params = "error", ["username already exists"]

    else:
        # update table
        cursor.execute("INSERT INTO users (username, pswd) VALUES (?, ?)", (username, password))
        connection.commit()

        cmd, params = 'success', []

    data_to_send[current_socket].append(build_msg(cmd=cmd, params=params, key=socket_to_key[current_socket]))

    cursor.close()
    connection.close()


def handle_logout(current_socket):
    if current_socket not in logged_users.keys():
        cmd, params = 'error', ['user not logged in']

    else:
        del logged_users[current_socket]
        cmd, params = 'success', []

    data_to_send[current_socket].append(build_msg(cmd=cmd, params=params, key=socket_to_key[current_socket]))


def handle_joinroom(current_socket, room):
    user_joined = logged_users[current_socket]

    # create new room if the given room doesn't exist
    if room not in sockets_in_rooms.keys():
        sockets_in_rooms[room] = []

    # create a list of the usernames in the room
    usernames_list = [logged_users[sock] for sock in sockets_in_rooms[room]]
    usernames_list = ','.join(usernames_list)

    for sock in sockets_in_rooms[room]:
        data_to_send[sock].append(build_msg(cmd='clientjoined', params=[user_joined], key=socket_to_key[sock]))

    # add new user to the list of the sockets in the room
    sockets_in_rooms[room].append(current_socket)

    data_to_send[current_socket].append(
        build_msg(cmd='usersinroom', params=[usernames_list], key=socket_to_key[current_socket]))


def handle_leaveroom(current_socket, room):
    # get the username
    user_left = logged_users[current_socket]

    for sock in sockets_in_rooms[room]:
        if sock is current_socket:
            data_to_send[sock].append(build_msg(cmd='success', params=[], key=socket_to_key[sock]))

        else:
            data_to_send[sock].append(build_msg(cmd='clientleft', params=[user_left], key=socket_to_key[sock]))

    # remove the socket from the sockets in room list
    sockets_in_rooms[room].remove(current_socket)


def handle_sendmsg(current_socket, room, msg_content):
    sender_username = logged_users[current_socket]
    for sock in sockets_in_rooms[room]:
        if sock is current_socket:
            data_to_send[sock].append(build_msg(cmd='recvmsg', params=['You', msg_content], key=socket_to_key[sock]))
        else:
            data_to_send[sock].append(build_msg(cmd='recvmsg', params=[sender_username, msg_content], key=socket_to_key[sock]))



def main(ip):
    setup_database()
    server_socket = setup_socket(ip)

    while True:
        # using select to create 2 lists. ready_to_read - a list of sockets which sent something
        # ready_to_write - a list of client sockets ready to receive data from the server
        ready_to_read, ready_to_write, _ = select.select([server_socket] + client_sockets, client_sockets, [])
        # print(data_to_send)
        for current_socket in ready_to_read:
            # handle a new client connecting
            if current_socket is server_socket:
                handle_new_connection(current_socket)
                
                

            else:
                # handle an existing user sending something. taking user who crashed under consideration
                try:
                    data = current_socket.recv(BUFFER_SIZE)
                    cmd, content = parse_data(data, socket_to_key[current_socket])
                    print(data)

                except OSError:
                    handle_disconected_client(current_socket)

                except NotProtocolException:
                    handle_disconected_client(current_socket)
                    current_socket.close()
                else:
                    # handle data recieved from user based on its command and params
                    if cmd == 'login':
                        username, password = content
                        handle_login(current_socket, username, password)

                    elif cmd == 'signup':
                        username, password = content
                        handle_signup(current_socket, username, password)

                    elif cmd == 'logout':
                        handle_logout(current_socket)

                    elif cmd == 'joinroom':
                        room = content[0]
                        handle_joinroom(current_socket, room)

                    elif cmd == 'leaveroom':
                        room = content[0]
                        handle_leaveroom(current_socket, room)

                    elif cmd == 'sendmsg':
                        room, msg_conetnt = content
                        handle_sendmsg(current_socket, room, msg_conetnt)

                    # elif cmd == 'publickey':
                    #     public_key = int(content[0])
                    #     handle_publickey(client_address, public_key)

        # looping over the client sockets which are ready to receive data,
        for current_socket in ready_to_write:
            # check if the client is still connected before the data is being sent
            if current_socket in data_to_send:
                for to_send in data_to_send[current_socket]:
                    print(to_send)
                    try:
                        current_socket.send(to_send)

                    except OSError:
                        handle_disconected_client(current_socket)

                data_to_send[current_socket] = []


if __name__ == '__main__':
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    main(ip)
