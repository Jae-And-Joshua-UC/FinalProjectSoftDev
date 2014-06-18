from pymongo import MongoClient
import datetime

c = MongoClient()


def admin(n):
    return c.users.Collections.find({"id":int(n),"admin":1}).count() == 1

# n = id, returns dictionary
def getUser(n):
    return c.users.Collections.find_one({"id":int(n)})

def getPost(n):
    return c.posts.Collections.find_one({"id":int(n)})

def getThread(n):
    return c.threads.Collections.find_one({"id":int(n)})

def getForum(n):
    return c.forums.Collections.find_one({"id":int(n)})


def threadPostCount(n):
    return c.posts.Collections.find({"tid":n}).count()

def forumThreadCount(n):
    return c.threads.Collections.find({"fid":n}).count()

def forumPostCount(n):
    r = 0
    for x in c.threads.Collections.find({"fid":n}):
        r += c.posts.Collections.find({"tid":x['id']}).count()
    return r


def lastPostInfoForum(n):
    cp = -1
    th = []
    for x in c.threads.Collections.find({"fid":n}):
        pd = c.posts.Collections.find({"tid":x['id']}).sort("id",-1).limit(1)[0]['id']
        if pd > cp:
            cp = pd
            th = [x['id'],x['title']]

    if cp >= 0:
        a = c.posts.Collections.find_one({"id":cp})
        return {
            "uid":a["uid"],
            "tid":th[0],
            "title":th[1],
            "username":getUser(a["uid"])["username"],
            "date":a["date"]
            }
    else:
        return None




def lastPostInfo(n):
    a = c.posts.Collections.find({"tid":n}).sort("id",-1).limit(1)[0]
    return {
        "uid":a["uid"],
        "username":getUser(a["uid"])["username"],
        "date":a["date"]
        }

# CREATION
def createPost(uid, tid, content):
    # tid = Thread ID
    # content = post content
    p = c.posts.Collections.find()
    if p.count() == 0:
        pid = 1
    else:
        pid = p.sort("id",-1).limit(1)[0]["id"]+1
    c.posts.Collections.insert({
            "id":pid,
            "uid":uid,
            "tid":tid,
            "hid":0,
            "date":datetime.datetime.now(),
            "content":content
            })
    return pid

def createThread(uid, fid, title, desc, content):
    # tid = Thread ID
    # content = post content
    t = c.threads.Collections.find()
    if t.count() == 0:
        tid = 1
    else:
        tid = t.sort("id",-1).limit(1)[0]["id"]+1
    c.threads.Collections.insert({
            "id":tid,
            "uid":uid,
            "fid":fid,
            "hid":0,
            "lock":0,
            "date":datetime.datetime.now(),
            "title":title,
            "desc":desc
            })
    pid = createPost(uid, tid, content)
    
    # in case two people post at the exact same time, avoid any conflict
    c.threads.Collections.update({"id":tid},{"$set":{"pid":pid}})
    return tid

def editPost(uid, pid, content):
    c.posts.Collections.update({"id":pid},{"$set":{"content":content,"editdate":datetime.datetime.now(),"edituid":uid}})

def edittitle(tid, title, desc):
    c.threads.Collections.update({"id":tid},{"$set":{"title":title,"desc":desc}})



# admin tools
def delthread(tid):
    c.threads.Collections.remove({"id":tid})
    c.posts.Collections.remove({"tid":tid})

def delpost(pid):
    c.posts.Collections.remove({"id":pid})

def hidepost(pid):
    c.posts.Collections.update({"id":pid},{"$set":{"hid":1}})
def unhidepost(pid):
    c.posts.Collections.update({"id":pid},{"$set":{"hid":0}})
def hidethread(pid):
    c.threads.Collections.update({"id":pid},{"$set":{"hid":1}})
def unhidethread(pid):
    c.threads.Collections.update({"id":pid},{"$set":{"hid":0}})
def lockthread(pid):
    c.threads.Collections.update({"id":pid},{"$set":{"lock":1}})
def unlockthread(pid):
    c.threads.Collections.update({"id":pid},{"$set":{"lock":0}})


def nav(stuff):
    r = '<ol class="breadcrumb">'

    for x in stuff:
        if len(x) == 1:
            r += '<li class="active">%s</li>'%(x[0])
        else:
            r += '<li><a href="%s">%s</a></li>'%(x[0],x[1])

    r += '</ol>'
    return r

