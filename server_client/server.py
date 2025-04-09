import socket
from server_client.do_connect import connect_to_network


SERVER_IP = connect_to_network()
SERVER_PORT = 8000
BUFFER_SIZE = 1024

UDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPServer.bind((SERVER_IP, SERVER_PORT))




