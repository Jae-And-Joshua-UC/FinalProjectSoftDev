from pymongo import MongoClient
import hashlib
from flask import session
c = MongoClient()
db = c.users



def encrypt(n):
    return hashlib.sha224(n).hexdigest()

def login(username,password):
    user = db.Collections.find_one({'username':username, 'password':encrypt(password)})
    if user:
        return user
    else:
        return None

def register(username,password):
    if db.Collections.find({'username':username}).count() == 0:
        user = db.Collections.count()+1
        db.Collections.insert({
                'id':user,
                'username':username,
                'password':encrypt(password),
                'admin':0})
        return user
    else:
        return False


