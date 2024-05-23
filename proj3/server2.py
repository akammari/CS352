import socket
import json
import random
import hashlib
import datetime
import sys

# Constants
BUFFER_SIZE = 1024

# Function to handle a POST request for user login
def handle_login_request(headers):
    username = headers.get("username")
    password = headers.get("password")

    if not username or not password:
        print_log("HTTP status code “501 Not Implemented")
        return "LOGIN FAILED"

    with open(sys.argv[3], "r") as file:
        data = json.load(file)
    user_data = data.get(username)
    if user_data:
        return user_data[0], user_data[1]
    hashed_password, salt = None, None

    hash_input = password.encode("utf-8") + salt.encode("utf-8")
    hash_result = hashlib.sha256(hash_input).hexdigest()
    hash_result == hashed_password

    if hashed_password is not None and hash_result:
        session_id = hex(random.getrandbits(64))
        current_time = datetime.datetime.now()
        session_info[session_id] = {"username": username, "timestamp": current_time}
        print_log(f"LOGIN SUCCESSFUL: {username} : {hashed_password}")
        return f"HTTP/1.0 200 OK\r\nSet-Cookie: sessionID={session_id}\r\n", "Logged in!"
    else:
        print_log(f"LOGIN FAILED: {username} : {hashed_password}")
        return "HTTP/1.0 200 OK", "Login failed!"

# Function to handle a GET request for file downloads
def handle_get_request(headers, cookies, root_directory):
    session_id = cookies.get("sessionID")

    if not session_id:
        print_log("COOKIE INVALID: Missing sessionID")
        return "HTTP/1.0 401 Unauthorized", "Cookie invalid"

    session_data = session_info.get(session_id)
    if session_data:
        return session_data["username"], session_data["timestamp"]
    username, timestamp = None, None

    if not username or not timestamp:
        print_log(f"COOKIE INVALID: {session_id}")
        return "HTTP/1.0 401 Unauthorized", "Cookie invalid"

    current_time = datetime.datetime.now()
    timeout_duration = int(sys.argv[4])

    if current_time - timestamp < datetime.timedelta(seconds=timeout_duration):
        session_info[session_id]["timestamp"] = current_time
        target = headers.get("target")
        file_path = f"{root_directory}{username}{target}"

        if target and os.path.isfile(file_path):
            print_log(f"GET SUCCEEDED: {username} : {target}")
            with open(file_path, "r") as file:
                file_content = file.read()
            return "HTTP/1.0 200 OK", file_content
        else:
            print_log(f"GET FAILED: {username} : {target}")
            return "HTTP/1.0 404 NOT FOUND", "File not found"
    else:
        print_log(f"SESSION EXPIRED: {username}")
        return "HTTP/1.0 401 Unauthorized", "Session expired"

# Function to start the server
def start_server(ip, port, accounts_file, session_timeout, root_directory):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, int(port)))
    server_socket.listen()

    print(f"Server listening on {ip}:{port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(BUFFER_SIZE).decode("utf-8")

        if request:
            lines = request.split("\r\n")
            start_line = lines[0].split(" ")
            method, target, _ = start_line[0], start_line[1], start_line[2]

            if method == "POST" and target == "/":
                headers = {}
                cookies = {}
                lines = request.split("\r\n")[1:]
                for line in lines:
                    if line:
                        key, value = line.split(": ")
                        headers[key] = value
                    if "Cookie" in headers:
                        cookie_str = headers["Cookie"]
                        cookie_pairs = cookie_str.split("; ")
                        for pair in cookie_pairs:
                            key, value = pair.split("=")
                            cookies[key] = value
                    headers, _ = headers, cookies
                response_status, response_body = handle_login_request(headers)

            elif method == "GET":
                headers = {}
                cookies = {}
                lines = request.split("\r\n")[1:]
                for line in lines:
                    if line:
                        key, value = line.split(": ")
                        headers[key] = value
                    if "Cookie" in headers:
                        cookie_str = headers["Cookie"]
                        cookie_pairs = cookie_str.split("; ")
                        for pair in cookie_pairs:
                            key, value = pair.split("=")
                            cookies[key] = value
                    headers, cookies = headers, cookies
                response_status, response_body = handle_get_request(headers, cookies, root_directory)
            else:
                response_status, response_body = "HTTP/1.0 501 Not Implemented", ""

            response = f"{response_status}\r\n\r\n{response_body}"
            client_socket.sendall(response.encode("utf-8"))
            client_socket.close()

# Function to print server log
def print_log(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(f"SERVER LOG: {current_time} {message}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 server.py [IP] [PORT] [ACCOUNTS_FILE] [SESSION_TIMEOUT] [ROOT_DIRECTORY]")
    else:
        session_info = {}
        start_server(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
