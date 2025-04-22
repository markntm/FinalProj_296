import socket


"""Likely do not need this as everything is being run by frontend HTML"""
SERVER_ADDRESS = ('127.0.0.1', 8000)  # SERVER IP_ADD, PORT NUM
BUFFER_SIZE = 1024
UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
