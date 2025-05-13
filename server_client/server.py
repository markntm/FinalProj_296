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
    "motor_open_time1": "?",
    "motor_open_time2": "?",

    "servo_door_state": "?",
    "servo_open_time1": "?",
    "servo_open_time2": "?"
}


def setup_devices(pr, wl, g, m, s):
    """Link the devices to the server module."""
    global photo_resistor, water_level, gate, motor, servo
    photo_resistor = pr
    water_level = wl
    gate = g
    motor = m
    servo = s


def webpage():
    html = "<html><head><title>Chicken Coop Tracker</title></head><body>"

    # Chicken Tracker Section
    html += "<h2>Chicken Tracker</h2>"
    html += "<p>Current count inside: " + str(sensor_cache["inside"]) + "</p>"
    html += "<p>Current count outside: " + str(sensor_cache["outside"]) + "</p>"
    html += "<p>Gate Height: " + str(sensor_cache["height"]) + " cm</p>"
    html += "<p>Chicken Height: " + str(sensor_cache["chicken_height"]) + " cm</p>"

    html += """<form action="/calibrate_sonar"><button type="submit">Calibrate Gate Idle Distance</button></form><br>"""

    html += """<form action="/" method="get">
                   <label for="chicken_height">Set Chicken Height</label>
                   <input type="number" id="chicken_height" name="CHICKEN_HEIGHT">
                   <input type="submit" value="Submit">
               </form><br>"""

    html += """<form action="/" method="get">
                   <label for="reset_chicken_count">Reset Number of Chickens Inside</label>
                   <input type="number" id="reset_chicken_count" name="CHICKEN_COUNT">
                   <input type="submit" value="Submit">
               </form><br>"""

    # Water Level Tracker Section
    html += "<h2>Water Level Tracker</h2>"
    html += "<p>Current State: " + str(sensor_cache["state"]) + "</p>"
    html += "<p>Current Water Level: " + str(sensor_cache["water_level"]) + " cm</p>"
    html += "<p>Low Water Level: " + str(sensor_cache["low"]) + " cm</p>"
    html += "<p>Empty Water Level: " + str(sensor_cache["empty"]) + " cm</p>"
    html += ('<form action="/calibrate_low_water_level"><button type="submit">Calibrate Low Water Threshold</button></form><br>')
    html += ('<form action="/calibrate_empty_water_level"><button type="submit">Calibrate Empty Water Threshold</button></form><br>')

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
    html += "<p>Open Times: " + str(sensor_cache["motor_open_time1"]) + ", " + str(sensor_cache["motor_open_time2"]) + "</p>"
    html += ('<form action="/" method="get"><label for="motor_open1">Set Motor Open Time1 (HH:MM)</label>'
             '<input type="text" id="motor_open1" name="MOTOR_OPEN1">'
             '<input type="submit" value="Submit"></form><br>')
    html += ('<form action="/" method="get"><label for="motor_open2">Set Motor Open Time2 (HH:MM)</label>'
             '<input type="text" id="motor_open2" name="MOTOR_OPEN2">'
             '<input type="submit" value="Submit"></form><br>')

    # Servo door Tracker Section
    html += "<h2>Servo Door</h2>"
    html += "<p>Current State: " + str(sensor_cache["servo_door_state"]) + "</p>"
    html += "<p>Open Times: " + str(sensor_cache["servo_open_time1"]) + ", " + str(sensor_cache["servo_open_time2"]) + "</p>"
    html += ('<form action="/" method="get"><label for="servo_open1">Set Servo Open Time1 (HH:MM)</label>'
             '<input type="text" id="servo_open1" name="SERVO_OPEN1">'
             '<input type="submit" value="Submit"></form><br>')
    html += ('<form action="/" method="get"><label for="servo_open2">Set Servo Open Time2 (HH:MM)</label>'
             '<input type="text" id="servo_open2" name="SERVO_OPEN2">'
             '<input type="submit" value="Submit"></form><br>')

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
                        value = value.replace('+', ' ')
                        value = value.replace('%3A', ':').replace('%3a', ':')  # Decode colon
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

                if "MOTOR_OPEN1" in params and motor:
                    motor.set_open_time1(params["MOTOR_OPEN1"])

                if "MOTOR_OPEN2" in params and motor:
                    motor.set_open_time2(params["MOTOR_OPEN2"])

                if "SERVO_OPEN1" in params and servo:
                    servo.set_open_time1(params["SERVO_OPEN1"])

                if "SERVO_OPEN2" in params and servo:
                    servo.set_open_time2(params["SERVO_OPEN2"])

            # Handle the GET request paths (button)
            if "GET /calibrate_sonar" in request and gate:
                print("Calibrating sonar sensors...")
                gate.calibrate_sensors()

            # Water level sensor calibration
            if "GET /calibrate_low_water_level" in request and water_level:
                print("Calibrating LOW water threshold...")
                success = water_level.init_low_threshold()
                if success:
                    sensor_cache["low"] = water_level.low_threshold

            if "GET /calibrate_empty_water_level" in request and water_level:
                print("Calibrating EMPTY water threshold...")
                success = water_level.init_empty_threshold()
                if success:
                    sensor_cache["empty"] = water_level.empty_threshold

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
