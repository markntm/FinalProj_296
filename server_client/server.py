from server_client.do_connect import connect_to_network
from http.server import HTTPServer, BaseHTTPRequestHandler

# server consts
SERVER_PORT = 8000
BUFFER_SIZE = 1024

# Default Parameters
photo_resistor = None
water_level = None
gate = None


def setup_devices(pr, wl, g):
    global photo_resistor, water_level, gate
    photo_resistor = pr
    water_level = wl
    gate = g


def load_index_html():
    """Converting index.html to response format"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error Loading HTML</h1>"


def web_page(
    inside="?", outside="?", height="?", chicken_height="?",
    state="?", water_level="?", low="?", empty="?",
    is_day="?", sunrise_time="?", sunset_time="?", light_threshold="?"
):
    """Creating response to be sent to HTML"""
    html = load_index_html()
    replacements = {
        "{{ inside }}": str(inside),
        "{{ outside }}": str(outside),
        "{{ height }}": str(height),
        "{{ chicken-height }}": str(chicken_height),
        "{{ state }}": str(state),
        "{{ water-level }}": str(water_level),
        "{{ low }}": str(low),
        "{{ empty }}": str(empty),
        "{{ is-day }}": str(is_day),
        "{{ sunrise-time }}": str(sunrise_time),
        "{{ sunset-time }}": str(sunset_time),
        "{{ light-threshold }}": str(light_threshold),
    }
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/init_photo":
            photo_resistor.init_threshold()
        elif self.path == '/calibrate_low_water_level':
            water_level.init_low_threshold()
        elif self.path == '/calibrate_empty_water_level':
            water_level.init_empty_threshold()
        elif self.path == '/calibrate_sonar':
            gate.calibrate_sensors()
        else:
            pass

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Placeholder values for inside/outside — replace with real sensor values
        response = web_page(inside=gate.get_inside_count(),
                            outside=gate.get_outside_count(),
                            height=gate.get_gate_height(),
                            chicken_height=gate.get_chicken_height(),
                            state=water_level.get_state(),
                            water_level=water_level.get_current_level(),
                            low=water_level.get_low_threshold(),
                            empty=water_level.get_empty_threshold(),
                            is_day=photo_resistor.is_day(),
                            sunrise_time=photo_resistor.get_sunrise_time(),
                            sunset_time=photo_resistor.get_sunset_time(),
                            light_threshold=photo_resistor.get_threshold())
        self.wfile.write(response.encode())


def run_server():
    SERVER_IP = connect_to_network()
    server_address = (SERVER_IP, SERVER_PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running at http://localhost:{SERVER_PORT}")
    httpd.serve_forever()
