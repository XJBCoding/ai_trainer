from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import pymongo
from datetime import datetime, timedelta
import random

client = pymongo.MongoClient("mongodb+srv://kunjian:iotproject@cluster0-ttnra.mongodb.net/test?retryWrites=true")
mydb = client["IoTProject"]
status = 0

def signin(id, password):
    global mydb, status
    profile = mydb['Profile']
    if profile.find_one({'userid': id}) is None:
        return "Account does not exist"
    else:
        if password == profile.find_one({"userid": id})["password"]:
            status = 1
            return "Successfully sign in"
        else:
            return "The password does not match our record"
            
def signout():
	global status

id = None
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET
    global id
    def do_POST(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        body = body.decode('utf-8')
        request = re.findall(r'(.*)\n', body)[0]
        userid = re.findall(request + '\n(.*)', body)[0]
        id = userid
        message = ""
        if request == "signin":
            password = re.findall(userid + '\n(.*)', body)[0]
            message = signin(userid, password)
        elif request == "signout":
            print("hhhh")
            signout()
        else:
            message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

def run_server():
    global id
    print('starting server...')
    message = ""
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('129.236.232.99', 8080)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    #while message != "Successfully sign in":
    #    message = httpd.handle()
    #    print(message)
    while status==0:
        httpd.handle_request()
    return 1,id

