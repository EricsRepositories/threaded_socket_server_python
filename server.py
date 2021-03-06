import threading
import socket
import os
import signal

# todo: headers for server socket as import (classed data)
#       function to print strings at equal start points
#       make instruction  "How many?"
#       allow clients to close the connection with a message
#       swap ip with alias for the broadcast
#       create class files
#       add a sys.stdout log file
#       add a ttyl for failed attempts
#       add data cleansing methods
#       handle threads
#       add a server restart method
#       add server shutdown and restart commands
#       make an http and https connection list
#       needs http header functionality (should probably be a class)

ascii_format = 'ascii'


all_ascii_connections = []
all_ascii_aliases = []
all_web_connections = []


def broadcast(broadcast_group, message):
    for connection in broadcast_group:
        try:
            connection.send(message)
        except:
            continue

def remove_ascii_connection(connection):
    index = all_ascii_connections.index(connection)
    alias = all_ascii_aliases[index]
    broadcast(all_ascii_connections, "~ connection ~ {} is no longer connected.\n".format(alias).encode(ascii_format))
    all_ascii_connections.remove(connection)
    all_ascii_aliases.remove(alias)
    connection.close()

def close_all_connections():
    for connection in all_ascii_connections:
        connection.close()
    all_ascii_connections[:]
    all_ascii_aliases[:]
    for connection in all_web_connections:
        connection.close()
    all_web_connections[:]

def shut_down_server():
    close_all_connections()
    ascii_socket.close()
    web_socket.close()
    print("The server shutdown has completed. Attempting to exit the shell.")
    os.kill(os.getpid(), signal.SIGTERM)

################
# Server instruction headers:

close_instruction = 'close'.encode(ascii_format)
server_stats_instruction = 'how many'.encode(ascii_format)
shutdown_server_instruction = 'shutdown the server'.encode(ascii_format)

################

def an_individual_ascii_connection(connection, connection_address):
    index = all_ascii_connections.index(connection)
    alias = all_ascii_aliases[index].encode(ascii_format)
    connected = True
    while connected:
        try:
            message = connection.recv(1024)
            broadcast_message = alias + b": " + message + b"\n"
            print("{} said: {}".format(connection_address, message))
            print("{} was sent as a full broadcast\n".format(broadcast_message))
            broadcast(all_ascii_connections, broadcast_message)
            if message == close_instruction:
                user_goodbye = "~ external ~ {} closed their connection.\n".format(alias).encode(ascii_format)
                print(user_goodbye)
                broadcast(all_ascii_connections, user_goodbye)
                connected = False
            if message == server_stats_instruction:
                connection.send("~ count ~ There is/are {} active connection/s.\n".format(threading.activeCount() - 1).encode(ascii_format))
            if message == shutdown_server_instruction:
                print("A message was received that shuts down the server.")
                shut_down_server()
        except:
            connected = False
    remove_ascii_connection(connection)




ip_server = socket.gethostbyname(socket.gethostname())
port_ascii_socket = 10000
port_web_socket = 10001

ascii_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# (opt/reuse) allows server restart using the same port
ascii_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ascii_socket.bind((ip_server, port_ascii_socket))

web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# (opt/reuse) allows server restart using the same port
web_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
web_socket.bind((ip_server, port_web_socket))




###########
# Threads #
###########

def ascii_connections_route():

    ascii_socket.listen(16)
    print("\n~ listen ~ The ascii server is listening on {}:{}\n".format(ip_server, port_ascii_socket))

    while True:

        ascii_client, ascii_client_address = ascii_socket.accept()
        
        print("A computer successfully connected to the chat server from {}.".format(str(ascii_client_address)))

        ascii_client.send('send_an_alias'.encode(ascii_format))
        alias = ascii_client.recv(1024).decode(ascii_format)

        print("New connection alias is {}\n".format(alias))
        all_ascii_aliases.append(alias)
        all_ascii_connections.append(ascii_client)

        broadcast(all_ascii_connections, "{} joined the chat.\n".format(alias).encode(ascii_format))
        ascii_client.send('You have successfully connected.\n'.encode(ascii_format))

        # Add address to args
        ascii_thread = threading.Thread(target=an_individual_ascii_connection, args=(ascii_client, ascii_client_address))
        ascii_thread.start()

def web_server_connections_route():

    web_socket.listen(16)
    print("\n~ listen ~ The web server is listening on {}:{}\n".format(ip_server, port_web_socket))

    while True:

        web_socket_connection_to_client, web_socket_client_address = web_socket.accept()
        print("A computer successfully connected to the web server from {}.".format(str(web_socket_client_address)))
        all_web_connections.append(web_socket_connection_to_client)

        message = web_socket_connection_to_client.recv(1024)
        try:
            filename = message.split()[1]
            print(filename)
            information = open(filename[1:])
            file_stream = information.read()
            web_socket_connection_to_client.send("HTTP/1.1 200 OK\r\n\r\n")
        
            for i in range(0, len(file_stream)):
                web_socket_connection_to_client.send(file_stream[i])
            web_socket_connection_to_client.send("\r\n")

        except Exception as e:
            print("~ web ~ There was a file error from the request\n {}".format(e))
            continue
        web_socket_connection_to_client.close()




# Thread assignments

def start_routing():

    close_all_connections()
    
    ascii_socket_thread = threading.Thread(target=ascii_connections_route, args=())
    ascii_socket_thread.start()
    
    web_socket_thread = threading.Thread(target=web_server_connections_route, args=())
    web_socket_thread.start()




#
#
#
#
start_routing()