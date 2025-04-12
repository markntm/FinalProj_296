import socket
from server_client.do_connect import connect_to_network

SERVER_PORT = 8000
BUFFER_SIZE = 1024


def server_stuff():
    SERVER_IP = connect_to_network()
    UDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServer.bind((SERVER_IP, SERVER_PORT))
    UDPServer.listen(1)
    return UDPServer


def load_index_html():
    """Converting index.html to response format"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error Loading HTML</h1>"


def web_page(inside, outside):
    """Creating response"""
    html = load_index_html()
    html = html.replace("{{inside}}", str(inside))
    html = html.replace("{{outside}}", str(outside))
    return html


def run_server(photo_resistor, water_level, gate):
    UDPServer = server_stuff()

    while True:
        try:
            conn, addr = UDPServer.accept()
            print("Got a connection from", addr)
            request = conn.recv(BUFFER_SIZE).decode()
            print("Request:", request)

            response = web_page()

            if "GET /init_photo" in request:
                photo_resistor.init_threshold()
            elif "GET /calibrate_low_water_level" in request:
                water_level.init_low_threshold()
            elif "GET /calibrate_empty_water_level" in request:
                water_level.init_empty_threshold()
            elif "GET /calibrate_sonar" in request:
                gate.calibrate_sensors()

            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except OSError as e:
            conn.close()
            print("Connection closed due to error:", e)


