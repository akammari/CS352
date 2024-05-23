import socket
import json
import random
import datetime
import hashlib
import sys

#Function to handle a POST request for user login:
def post(requestheaders, accounts, session):
    username = requestheaders.get("username")
    password = requestheaders.get("password")

    if not username or not password:
        log("LOGIN FAILED")
        return "501 Not Implemented", "LOGIN FAILED"

    if username in accounts and checkpassword(password, accounts[username]):
        sessionID = hex(random.getrandbits(64))
        session[sessionID] = {"username": username, "timestamp": datetime.datetime.now()}
        log(f"LOGIN SUCCESSFUL: {username} : {password}")
        return "200 OK", f"Set-Cookie: {'sessionID'}={sessionID}\nLogged in!"

    log(f"LOGIN FAILED: {username} : {password}")
    return "200 OK", "Login failed!"

def checkpassword(plaintext, data):
    storedpassword, salt = data
    inputpassword = hashlib.sha256((plaintext + salt).encode()).hexdigest()
    return inputpassword == storedpassword

#Function to handle a GET request for file downloads:
def get(requestheaders, session, root_directory):
    cookies = requestheaders.get("Cookie", "").split("; ")
    sessionID = None

    for cookie in cookies:
        name, value = cookie.split("=")
        if name == 'sessionID':
            sessionID = value

    if not sessionID or sessionID not in session:
        log("COOKIE INVALID")
        return "401 Unauthorized", ""

    current = session[sessionID]
    username = current["username"]
    timestamp = current["timestamp"]

    if (datetime.datetime.now() - timestamp).seconds > SESSION_TIMEOUT:
        log("SESSION EXPIRED")
        return "401 Unauthorized", "Session expired!"

    session[sessionID]["timestamp"] = datetime.datetime.now()

    requesttarget = requestheaders.get("Request-Target", "/")
    filepath = f"{root_directory}{username}{requesttarget}"

    try:
        with open(filepath, "r") as file:
            filecontents = file.read()
            log(f"GET SUCCEEDED: {username} : {requesttarget}")
            return "200 OK", filecontents
        
    except FileNotFoundError:
        log(f"GET FAILED: {username} : {requesttarget}")
        return "404 NOT FOUND", ""
    
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(f"SERVER LOG: {timestamp} {message}")

#Function to start the server:
def start(ip, port, accounts_file, session_timeout, root_directory):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((ip, port))
    serversocket.listen()

    with open(accounts_file, "r") as file:
        accounts_data = json.load(file)

    accounts = accounts_data
    
    session = {}

    while True:
        clientsocket, clientaddress = serversocket.accept()
        requestclient = clientsocket.recv(4096).decode("utf-8")

        if not requestclient:
            continue

        headers, body = requestclient.split("\r\n" + "\r\n", 1)
        requestheaders = ""

        headerlines = headers.split("\r\n")
        firstline = headerlines.pop(0)
        method, requesttarget, _ = firstline.split(" ")
        header_dict = {"Method": method, "Request-Target": requesttarget}

        for line in headerlines:
            key, value = line.split(": ")
            header_dict[key] = value
        
        requestheaders = header_dict

        method = requestheaders.get("Method")
        if method == "POST" and requestheaders.get("Request-Target") == "/":
            status, response = post(requestheaders, accounts, session)
        
        elif method == "GET":
            status, response = get(requestheaders, session, root_directory)
        
        else:
            status, response = "501 Not Implemented", ""

        response_headers = f"HTTP/1.0 {status}\n\n"
        clientsocket.sendall((response_headers + response).encode("utf-8"))
        clientsocket.close()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 server.py [IP] [PORT] [ACCOUNTS_FILE] [SESSION_TIMEOUT] [ROOT_DIRECTORY]")
        sys.exit(1)

    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    ACCOUNTS_FILE = sys.argv[3]
    SESSION_TIMEOUT = int(sys.argv[4])
    ROOT_DIRECTORY = sys.argv[5]

    start(IP, PORT, ACCOUNTS_FILE, SESSION_TIMEOUT, ROOT_DIRECTORY)