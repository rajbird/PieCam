import hmac
import os
import hashlib
import base64
import json
from collections import namedtuple

class user:
    def __init__(self, username, password, salt,authenticated):
        self.username = username
        self.password = password
        self.salt = salt
        self.authenticated = authenticated
    username = ""
    password = ""
    salt = ""
    authenticated  = ""


def generate_salt():
    salt = os.urandom(16)
    salt = base64.b64encode(salt)
    return str(salt)

def generate_signature(salt, secret_key, encoding):
    secret_key_bytes = bytes(secret_key, encoding)
    salt_bytes = bytes(salt, encoding)
    dig = hmac.new(secret_key_bytes, salt_bytes, hashlib.sha256).digest()
    signature = base64.b64encode(dig)
    return signature

def createUser(username, password, usersFile):
    salt = generate_salt()
    newUser = user(username,generate_signature(salt,password,"utf-8").decode("utf-8"),salt,"0")
    usersFile.seek(0, os.SEEK_END)
    json.dump(newUser.__dict__,usersFile)
    usersFile.write("\n")
    return newUser

def authenticateUser(username, password,usersFile):
    usersFile.seek(0, os.SEEK_SET)
    row = usersFile.readline()

    while(row != ""):
        newUser = json.loads(row)
        newUser = namedtuple('User', newUser.keys())(*newUser.values())
        newUser = user(newUser.username, newUser.password, newUser.salt, "0")
        if(newUser.username == username):
            if(newUser.password == generate_signature(newUser.salt,password,"utf-8").decode("utf-8")):
                newUser.authenticated = "1"
                break
            else:
                newUser.authenticated = "0"
        row = usersFile.readline()

    if(newUser.authenticated == "0"):
        print("Wrong username or password")
        return 0
    else:
        print("Authenticated")
        return newUser