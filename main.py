import _thread
import time
from machine import Pin
import network
import socket
from server_client import server


def load_index_html():
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error Loading HTML</h1>"


def web_page(inside, outside):
    html = load_index_html()
    html = html.replace("{{inside}}", str(inside))
    html = html.replace("{{outside}}", str(outside))
    return html


def core0_main():
    pass


def core1_server():
    UDPServer, BUFFER_SIZE = server.server_stuff()

    while True:
        conn, addr = UDPServer.accept()
        print("Got a connection from", addr)
        request = conn.recv(BUFFER_SIZE)
        request = str(request)

        response = web_page()
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n')
        conn.sendall(response)
        conn.close()

    pass


if __name__ == '__main__':
    _thread.start_new_thread(core1_server, ())
    core0_main()
