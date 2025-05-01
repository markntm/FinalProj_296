import socket
from server_client.do_connect import connect_to_network

# server consts
SERVER_PORT = 8000
BUFFER_SIZE = 1024

# Default Parameters
photo_resistor = None
water_level = None
gate = None


# Cached values
sensor_cache = {
    "inside": "?",
    "outside": "?",
    "height": "?",
    "chicken_height": "?",
    "state": "?",
    "water_level": "?",
    "low": "?",
    "empty": "?",
    "is_day": "?",
    "sunrise_time": "?",
    "sunset_time": "?",
    "light_threshold": "?"
}


def setup_devices(pr, wl, g):
    """Link the devices to the server module."""
    global photo_resistor, water_level, gate
    photo_resistor = pr
    water_level = wl
    gate = g


def load_index_html():
    """Converting index.html to response format"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except OSError:
        return "<h1>Error Loading HTML</h1>"


def webpage():
    """Creating response by filling in sensor values."""
    html = load_index_html()
    for key, value in {
        "{{ inside }}": str(sensor_cache["inside"]),
        "{{ outside }}": str(sensor_cache["outside"]),
        "{{ height }}": str(sensor_cache["height"]),
        "{{ chicken_height }}": str(sensor_cache["chicken_height"]),
        "{{ state }}": str(sensor_cache["state"]),
        "{{ water-level }}": str(sensor_cache["water_level"]),
        "{{ low }}": str(sensor_cache["low"]),
        "{{ empty }}": str(sensor_cache["empty"]),
        "{{ is-day }}": str(sensor_cache["is_day"]),
        "{{ sunrise-time }}": str(sensor_cache["sunrise_time"]),
        "{{ sunset-time }}": str(sensor_cache["sunset_time"]),
        "{{ light-threshold }}": str(sensor_cache["light_threshold"]),
    }.items():
        html = html.replace(key, str(value))
    return html


def open_socket():
    address = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(address)
        s.listen(1)
        return s
    except OSError as e:
        print("Socket error:", e)
        s.close()
        raise


def serve(server_socket):
    try:
        while True:
            print("Waiting for client...")
            client, addr = server_socket.accept()
            print("Client connected from", addr)
            request = client.recv(1024).decode('utf-8')
            print(f"Request received: \n{request}")

            # Handle the GET request paths
            if "GET /calibrate_sonar" in request:
                print("Calibrating sonar sensors...")
                if gate:
                    gate.calibrate_sensors()

                    # Refresh data (assumes gate.update() updates internal values)
            if gate:
                gate.update()
                # Optionally update sensor_cache with gate values
                try:
                    sensor_cache["height"] = gate.height
                    sensor_cache["chicken_height"] = gate.chicken_height
                    sensor_cache["inside"] = gate.count_inside
                    sensor_cache["outside"] = gate.count_outside
                except Exception as e:
                    print("Error updating sensor_cache:", e)

            html = webpage()

            client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            client.sendall(html)
            client.close()
    except KeyboardInterrupt:
        print("Server stopped manually.")
    except Exception as e:
        print("Server error:", e)
    finally:
        server_socket.close()
        print("Socket closed.")


def run_server():
    print("Core 1 Server: On")
    SERVER_IP = connect_to_network()

    if SERVER_IP is None:
        print("No Wi-Fi connection. Server cannot start.")
        print("Core 1 Server: Off")
        return  # Exit the server function safely

    server_socket = open_socket()
    print(f"Listening on http://{SERVER_IP}")
    serve(server_socket)
    print("Core 1 Server: Off")
