# Set your server IP and port
SERVER_IP="Localhost"
SERVER_PORT="8080"

# Variables for storing session cookies
SESSION_COOKIE=""

# Common curl options for HTTP/1.0 and connection close
CURL_OPTIONS="--http1.0 --connect-timeout 5 --max-time 10 --fail --silent"

#SESSION_COOKIE=$(curl -i -v -X POST -H "username: Richard" -H "password: 3TQI8TB39DFIMI6" "http://${SERVER_IP}:${SERVER_PORT}/" | grep -i 'Set-Cookie' | cut -d ' ' -f 2 | cut -d '=' -f 2)
#echo "\\nCookie (sessionID) for user: $SESSION_COOKIE"

#curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

# Test Case 1: No Username (POST at the root)
echo "Test Case 1: No Username"
curl -i -v -X POST -H "password: somepassword" "http://${SERVER_IP}:${SERVER_PORT}/" 

echo ""

# Test Case 2: No Password (POST at the root)
echo "Test Case 2: No Password"
curl -i -v -X POST -H "username: someuser" "http://${SERVER_IP}:${SERVER_PORT}/" 

echo ""

# Test Case 3: Username Incorrect (POST at the root)
echo "Test Case 3: Username Incorrect"
curl -i -v -X POST -H "username: wronguser" -H "password: 4W61E0D8P37GLLX" "http://${SERVER_IP}:${SERVER_PORT}/" 

echo ""

# Test Case 4: Password Incorrect (POST at the root)
echo "Test Case 4: Password Incorrect"
curl -i -v -X POST -H "username: Jerry" -H "password: wrongpassword" "http://${SERVER_IP}:${SERVER_PORT}/" 

echo ""

# Test Case 5: Username (1st username) correct/password correct (POST at the root)
echo "Test Case 5: Correct Username and Password"
curl -i -v -X POST -H "username: Jerry" -H "password: 4W61E0D8P37GLLX" "http://${SERVER_IP}:${SERVER_PORT}/" 

echo ""

# Test Case 6: Username (1st username) correct/password correct (POST at the root) -> Generate a new cookie
echo "Test Case 6: Generate a new cookie for the same user"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Jerry" -H "password: 4W61E0D8P37GLLX" "http://${SERVER_IP}:${SERVER_PORT}/") 


echo ""

# Test Case 7: Invalid Cookie (GET)
echo "Test Case 7: Invalid Cookie"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=invalidcookie" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

echo ""

# Test Case 8: Username (1st username) (GET filename for user 1 ) correct
echo "Test Case 8: Access file with valid cookie for user 1"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

echo ""

# Test Case 9: Username (2nd username) correct/password correct (POST)
echo "Test Case 9: Correct Username and Password for user 2"
SESSION_COOKIE=$(curl -i -v -X POST -H "username: Matthew" -H "password: 51HCPUQXYYQHNAI" "http://${SERVER_IP}:${SERVER_PORT}/") 

echo ""

# Test Case 10: GET file successful (GET filename for user 2 )
echo "Test Case 10: Access file with valid cookie for user 2"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

echo ""

# Test Case 11: GET file not found (GET FAIL)
echo "Test Case 11: GET File Not Found"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/nonexistentfile.txt"

echo ""

# Sleep for 6 seconds
echo "Sleeping for 6 seconds..."
sleep 6

# Test Case 12: Expired cookie with username 2 (GET filename for user 2)
echo "Test Case 12: Expired Cookie with User 2"
curl $CURL_OPTIONS -v -X GET -H "Cookie: sessionID=$SESSION_COOKIE" "http://${SERVER_IP}:${SERVER_PORT}/file.txt"

echo ""