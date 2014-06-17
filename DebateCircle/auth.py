from pymongo import MongoClient

c = MongoClient()

db=c.admin

def authorize(username, password):
    return len(list(db.Collections.find({'username':username, 'password':password}))) == 1
def userExists(username):
    return len(list(db.Collections.find({'username':username}))) == 1
def createUser(username, password):
    if not userExists(username):
        db.Collections.insert({'username':username, 'password':password})
        return True
    else:
        return False
