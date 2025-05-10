import socket
from server_client.do_connect import connect_to_network

# server consts
SERVER_PORT = 8000
BUFFER_SIZE = 1024

# Default Parameters
photo_resistor = None
water_level = None
gate = None
motor = None
servo = None

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
    "light_threshold": "?",

    "motor_door_state": "?",
    "motor_open_times": "?",
    "motor_close_times": "?",

    "servo_door_state": "?",
    "servo_open_times": "?",
    "servo_close_times": "?"
}


def setup_devices(pr, wl, g, m, s):
    """Link the devices to the server module."""
    global photo_resistor, water_level, gate, motor, servo
    photo_resistor = pr
    water_level = wl
    gate = g
    motor = m
    servo = s


# delete
def load_index_html():  # seeing if it can be replaced
    """Converting index.html to response format"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except OSError:
        return "<h1>Error Loading HTML</h1>"


# delete
def old_webpage():  # seeing if it can be replaced
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


def webpage():
    html = "<html><head><title>Chicken Coup Tracker</title></head><body>"

    # Chicken Tracker Section
    html += "<h2>Chicken Tracker</h2>"
    html += "<p>Current count inside: " + str(sensor_cache["inside"]) + "</p>"
    html += "<p>Current count outside: " + str(sensor_cache["outside"]) + "</p>"
    html += "<p>Gate Height: " + str(sensor_cache["height"]) + " cm</p>"
    html += "<p>Chicken Height: " + str(sensor_cache["chicken_height"]) + " cm</p>"

    html += """<form action="/calibrate_sonar"><button type="submit">Calibrate Gate Idle Distance</button></form><br>"""
    html += """<form><label for="chicken_height">Set Chicken Height</label>
                   <input type="text" id="chicken_height" name="CHICKEN_HEIGHT">
                   <input type="submit" value="submit"></form><br>"""
    html += """<form><label for="reset_chicken_count">Reset Number of Chickens Inside</label>
                   <input type="text" id="reset_chicken_count" name="CHICKEN_COUNT">
                   <input type="submit" value="submit"></form><br>"""

    # Water Level Tracker Section
    html += "<h2>Water Level Tracker</h2>"
    html += "<p>Current State: " + str(sensor_cache["state"]) + "</p>"
    html += "<p>Current Water Level: " + str(sensor_cache["water_level"]) + " cm</p>"
    html += "<p>Low Water Level: " + str(sensor_cache["low"]) + " cm</p>"
    html += "<p>Empty Water Level: " + str(sensor_cache["empty"]) + " cm</p>"
    html += ('<form action="/calibrate_low_water_level">'
             '<button type="submit">Calibrate Low Water Threshold</button></form><br>')
    html += ('<form action="/calibrate_empty_water_level">'
             '<button type="submit">Calibrate Empty Water Threshold</button></form><br>')

    # Light Level Tracker Section
    html += "<h2>Light Level Tracker</h2>"
    html += "<p>Currently Daytime: " + str(sensor_cache["is_day"]) + "</p>"
    html += "<p>Sunrise Time: " + str(sensor_cache["sunrise_time"]) + "</p>"
    html += "<p>Sunset Time: " + str(sensor_cache["sunset_time"]) + "</p>"
    html += "<p>Day-Night Threshold: " + str(sensor_cache["light_threshold"]) + "</p>"
    html += '<form action="/init_photo"><button type="submit">Calibrate Day-Night Threshold</button></form><br>'

    # Motor door Tracker Section
    html += "<h2>Motor Door</h2>"
    html += "<p>Current State: " + str(sensor_cache["motor_door_state"]) + "</p>"
    html += "<p>Open Times: " + str(sensor_cache["motor_open_times"]) + "</p>"
    html += "<p>Close Times: " + str(sensor_cache["motor_close_times"]) + "</p>"
    html += ('<form><label for="motor_open">Set Motor Open Time (HH:MM)</label>'
             '<input type="text" id="motor_open" name="MOTOR_OPEN">'
             '<input type="submit" value="submit"></form><br>')
    html += ('<form><label for="motor_close">Set Motor Close Time (HH:MM)</label>'
             '<input type="text" id="motor_close" name="MOTOR_CLOSE">'
             '<input type="submit" value="submit"></form><br>')

    # Servo door Tracker Section
    html += "<h2>Servo Door</h2>"
    html += "<p>Current State: " + str(sensor_cache["servo_door_state"]) + "</p>"
    html += "<p>Open Times: " + str(sensor_cache["servo_open_times"]) + "</p>"
    html += "<p>Close Times: " + str(sensor_cache["servo_close_times"]) + "</p>"
    html += ('<form><label for="servo_open">Set Servo Open Time (HH:MM)</label>'
             '<input type="text" id="servo_open" name="SERVO_OPEN">'
             '<input type="submit" value="submit"></form><br>')
    html += ('<form><label for="servo_close">Set Servo Close Time (HH:MM)</label>'
             '<input type="text" id="servo_close" name="SERVO_CLOSE">'
             '<input type="submit" value="submit"></form><br>')

    html += "</body></html>"
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

            # reads request
            request_line = request.split('\r\n')[0]
            print(f"Request line: {request_line}")

            # Parse GET parameters if present (key-value pair param)
            if "GET /?" in request_line:
                param_string = request_line.split("GET /?")[1].split(" ")[0]
                param_pairs = param_string.split("&")
                params = {}
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params[key] = value

                # Process CHICKEN_HEIGHT
                if "CHICKEN_HEIGHT" in params:
                    try:
                        height = int(params["CHICKEN_HEIGHT"])
                        print("New chicken height:", height)
                        if gate:
                            gate.chickenHeight = height
                    except:
                        print("Invalid CHICKEN_HEIGHT input")

                # Process CHICKEN_COUNT
                if "CHICKEN_COUNT" in params:
                    try:
                        count = int(params["CHICKEN_COUNT"])
                        print("Resetting chicken count to:", count)
                        if gate:
                            gate.reset_chicken_count(count)
                    except:
                        print("Invalid CHICKEN_COUNT input")

                if "MOTOR_OPEN" in params and motor:
                    motor.open_times = [params["MOTOR_OPEN"]]
                    print("Updated Motor Door open time:", motor.open_times)

                if "MOTOR_CLOSE" in params and motor:
                    motor.close_times = [params["MOTOR_CLOSE"]]
                    print("Updated Motor Door close time:", motor.close_times)

                if "SERVO_OPEN" in params and servo:
                    servo.open_times = [params["SERVO_OPEN"]]
                    print("Updated Servo Door open time:", servo.open_times)

                if "SERVO_CLOSE" in params and servo:
                    servo.close_times = [params["SERVO_CLOSE"]]
                    print("Updated Servo Door close time:", servo.close_times)

            # Handle the GET request paths (button)
            if "GET /calibrate_sonar" in request:
                print("Calibrating sonar sensors...")
                if gate:
                    gate.calibrate_sensors()

                    # Refresh data (assumes gate.update() updates internal values)
            if gate:
                gate.update()
                # Optionally update sensor_cache with gate values
                try:
                    sensor_cache["height"] = gate.innerSensor.idle_distance
                    sensor_cache["chicken_height"] = gate.chickenHeight
                    sensor_cache["inside"] = gate.inside_count
                    sensor_cache["outside"] = gate.outside_count
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
