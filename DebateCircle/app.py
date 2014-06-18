from flask import *
from pymongo import MongoClient


# my files
import config
import html
import utils
from utils import getUser, getThread, getForum, admin
import auth


app = Flask(__name__)
app.debug = True
app.secret_key = "key"
c = MongoClient()

fn = "Index"
def getFn():
    return fn
def getUID():
    try:
        return session["uid"]
    except:
        return -1

def page(body,u):
    return render_template("index.html",header=html.getHeader(u),body=body)

# LOGIN/REGISTER
@app.route("/login",methods=['GET','POST'])
def login():
    # type:
    # 1 = username/password combo does not exist
    if request.method == "POST":
        user = auth.login(request.form["username"],request.form["password"])
            
        if user:
            session["uid"] = user["id"]
            return redirect("/?type=3")
        else:
            return page(html.login(1),-1)
    else:
        return page(html.login(0),-1)


@app.route("/register",methods=['GET','POST'])
def register():
    # type:
    # 1 = username already in use
    # 2 = passwords don't match
    if request.method == "POST":
        if request.form["password"] == request.form["password2"]:
            result = auth.register(request.form["username"],request.form["password"])
            if result:
                session["uid"] = result
                return redirect("/?type=2")
            else:
                return page(html.register(1),-1)
        else:
            return page(html.register(2),-1)
    else:
        return page(html.register(0),-1)

@app.route("/logout")
def logout():
    session.pop("uid",None)
    return redirect("/?type=1")

@app.route("/")
def index():
    # type:
    # 1 = logged out
    # 2 = registered
    # 3 = logged in
    uid = getUID()
    nav = utils.nav([[fn]])
    r = ""

    r += '<div id="header">Forum</div>'
    r += nav

    tp = request.args.get("type")
    mes = ""
    if tp == '1':
        mes = "You have logged out."
    elif tp == '2':
        mes = "Account registration successful!"
    elif tp == '3':
        mes = "You have logged in."

    if mes:
        r += '<div class="alert alert-success"><strong>Success</strong>: %s</div>'%(mes)

    r += """
<table class="table" cellspacing="0">
<tr class="active">
<th>Forum Name</th>
<th class="f_num">Threads</th>
<th class="f_num">Posts</th>
<th class="f_last">Last Post</th>
"""
    for x in c.forums.Collections.find():
        r += html.forum(x)
    r += '</table>'
    
    r += """
<table class="table">
<tr class="active">
<th>Forum Statistics</th>
</tr>
<tr class="active">
<td>
Total Posts: <strong>%d</strong><br />
Total Threads: <strong>%d</strong><br />
Total Users: <strong>%d</strong>
</td>
</tr>
</table>"""%(c.posts.Collections.find().count(),c.threads.Collections.find().count(),c.users.Collections.find().count())




    r += nav


    return page(r,uid)


@app.route("/forum-<n>")
def forum(n):
    # type:
    # 1 = thread deleted
    uid = getUID()
    r = ""
    
    forum = getForum(n)
    if forum:

        nav = utils.nav([
                ["/",fn],
                [forum["name"]]
                ])

        options = ""
        if uid != -1:
            options = '<div class="options"><a href="newthread-%d" class="btn btn-primary"><span class="glyphicon glyphicon-plus"></span> Create New Thread</a></div>'%(forum['id'])

        r += '<div id="header">%s</div>'%(forum['name'])
        r += nav

        tp = request.args.get("type")
        mes = ""
        if tp == '1':
            mes = "Thread deleted."

        if mes:
            r += '<div class="alert alert-success"><strong>Success</strong>: %s</div>'%(mes)


        r += options
        r += """<table class="table" cellspacing="0">
<tr class="active"><th class="t_title">Thread Title</th><th class="t_author">Author</th><th class="t_num">Posts</th><th>Last Post</th></tr>
"""
        thr = c.threads.Collections.find({"fid":forum['id']})
        if thr.count() == 0:
            r += '<tr class="active"><td colspan="4">No threads exist in this forum</td></tr>'
        else:
            for x in thr:
                r += html.thread(x,admin(uid))
        r += '</table>'
        r += options
        r += nav

        return page(r,uid)


@app.route("/thread-<n>")
def thread(n):
    uid = getUID()


    r = ""

    thread = getThread(n)
    
    if thread:
        # if thread is hidden and cannot view
        if thread['hid'] and not admin(uid):
            return page(html.permissionDenied(),uid)

        posts = c.posts.Collections.find({"tid":thread['id']}).sort("id",1)
        # pages
        pg = 1
        p = request.args.get("page")
        if p:
            pg = int(p)

        pghtml = html.pages(pg,int((posts.count()-1)/config.postsPerPage())+1,"thread-%d?page="%(thread['id']))

        forum = getForum(thread["fid"])
        nav = utils.nav([
                ["/",fn],
                ["/forum-%d"%(forum['id']),forum["name"]],
                [thread["title"]]
                ])


        atools = ""



        # admin tools
        if admin(uid):
            atools += """
<table class="table">
<tr class="warning">
<td style="width:150px;text-align:center;font-weight:bold;">Administrative<br />Tools</td>
<td style="vertical-align:middle;">
<a href="edittitle-%d" class="btn btn-warning"><span class="glyphicon glyphicon-pencil"></span> Edit Thread Title</a>"""%(thread['id'])

            # lock/unlock
            if "lock" in thread.keys() and thread['lock']:
                atools += ' <a href="unlockthread-%d" class="btn btn-success"><span class="glyphicon glyphicon-lock"></span> Unlock Thread</a>'%(thread['id'])
            else:
                atools += ' <a href="lockthread-%d" class="btn btn-danger"><span class="glyphicon glyphicon-lock"></span> Lock Thread</a>'%(thread['id'])

            # hide/unhide
            if "hid" in thread.keys() and thread['hid']:
                atools += ' <a href="unhidethread-%d" class="btn btn-success"><span class="glyphicon glyphicon-eye-open"></span> Unhide Thread</a>'%(thread['id'])
            else:
                atools += ' <a href="hidethread-%d" class="btn btn-danger"><span class="glyphicon glyphicon-eye-close"></span> Hide Thread</a>'%(thread['id'])
            atools += """
<a href="delthread-%d" class="btn btn-danger deleteThread"><span class="glyphicon glyphicon-remove"></span> Delete Thread</a>
</td>
</tr>
</table>"""%(thread['id'])

        options = ""
        if uid != -1 and (not thread['lock'] or admin(uid)):
            options = '<div class="options"><a href="reply-%d" class="btn btn-primary"><span class="glyphicon glyphicon-plus"></span> Reply</a></div>'%(thread['id'])


        r += '<div id="header">%(title)s</div><div class="description">%(desc)s</div>'%(thread)

        r += '<div class="thread_info">'

        if thread['lock']:
            r += '<span class="alert alert-danger"><span class="glyphicon glyphicon-lock"></span> Locked</span>'
        if thread['hid']:
            r += '<span class="alert alert-danger"><span class="glyphicon glyphicon-eye-close"></span> Hidden</span>'
        
        r += '</div>'

        mes = request.args.get("type")
        if mes == '1':
            mes = "Thread title edited"
        elif mes == '2':
            mes = "Thread hidden"
        elif mes == '3':
            mes = "Thread unhidden"
        elif mes == '4':
            mes = "Thread locked"
        elif mes == '5':
            mes = "Thread unlocked"
        elif mes == '51':
            mes = "Post deleted"
        elif mes == '52':
            mes = "Post edited"



        r += nav
        if mes:
            r += '<div class="alert alert-success"><strong>Success:</strong> %s</div>'%(mes)
        r += atools
        r += pghtml
        r += options
        r += '<div id="posts">'


        ppp = config.postsPerPage()
        for x in range((pg-1)*ppp,min(pg*ppp,posts.count())):
            r += html.post(uid,posts[x])

        r += '</div>'
        r += options
        r += pghtml
        r += nav

        return page(r,uid)
    else:
        return page(html.threadDoesNotExist(),uid)


    





# CREATE NEW .....
# add post, n = tid
@app.route("/reply-<n>",methods=['GET','POST'])
def reply(n):
    uid = getUID()

    if uid == -1:
        return page(html.permissionDenied(),-1)
    if request.method == "POST":
        tid = int(request.form["tid"])
        thread = c.threads.Collections.find_one({"id":tid})
        
        if thread:
            if (not thread['hid'] and not thread['lock']) or admin(uid):
                utils.createPost(uid, tid, request.form["content"])
                return redirect("/thread-%d"%(tid))
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.threadDoesNotExist(),uid)
    else:
        r = ""
    
        thread = c.threads.Collections.find_one({"id":int(n)})
        if thread:
            if (not thread['hid'] and not thread['lock']) or admin(uid):
                r += html.reply(thread["id"])
                return page(r,uid)
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.threadDoesNotExist(),uid)

# new thread, n = tid
@app.route("/newthread-<n>",methods=['GET','POST'])
def newthread(n):
    uid = getUID()

    if uid == -1:
        return page(html.permissionDenied(),-1)

    if request.method == "POST":
        fid = int(request.form["fid"])
        forum = c.forums.Collections.find_one({"id":fid})
        
        if forum:
            tid = utils.createThread(uid, fid, request.form["title"], request.form["desc"], request.form["content"])
            return redirect("/thread-%d"%(tid))
        else:
            return page(html.forumDoesNotExist(),uid)
    else:
        r = ""
    
        forum = c.forums.Collections.find_one({"id":int(n)})
        if forum:
            r += html.newthread(forum["id"])
            return page(r,uid)
        else:
            return page(html.forumDoesNotExist(),uid)

@app.route("/editpost-<n>",methods=['GET','POST'])
def editpost(n):
    uid = getUID()

    if request.method == "POST":
        pid = int(request.form["pid"])
        post = c.posts.Collections.find_one({"id":pid})
        
        if post:
            if (uid == post["uid"] and not post['hid'] and not getThread(post['tid'])['hid']) or admin(uid):
                utils.editPost(uid, pid, request.form["content"])
                return redirect("/thread-%d?type=52"%(getThread(post["tid"])['id']))
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.postDoesNotExist(),uid)
    else:
        r = ""
    
        post = c.posts.Collections.find_one({"id":int(n)})
        if post:
            if (uid == post["uid"] and not post['hid'] and not getThread(post['tid'])['hid']) or admin(uid):
                r += html.editpost(post["id"])
                return page(r,uid)
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.postDoesNotExist(),uid)

@app.route("/edittitle-<n>",methods=['GET','POST'])
def edittitle(n):
    uid = getUID()

    if request.method == "POST":
        tid = int(request.form["tid"])
        thread = c.threads.Collections.find_one({"id":tid})
        
        if thread:
            if admin(uid):
                utils.edittitle(tid, request.form["title"], request.form["desc"])
                return redirect("/thread-%d?type=1"%(tid))
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.threadDoesNotExist(),uid)
    else:
        r = ""
    
        thread = c.threads.Collections.find_one({"id":int(n)})
        if thread:
            if admin(uid):
                r += html.edittitle(thread["id"])
                return page(r,uid)
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.threadDoesNotExist(),uid)


# admin tools
@app.route("/delthread-<n>",methods=['GET','POST'])
def delthread(n):
    uid = getUID()

    if request.method == "POST":
        tid = int(request.form["tid"])
        thread = c.threads.Collections.find_one({"id":tid})
        
        if thread:
            if admin(uid):
                utils.delthread(tid)
                if "ajax" in request.form:
                    return "/forum-%d?type=1"%(thread['fid'])
                else:
                    return redirect("/forum-%d?type=1"%(thread['fid']))
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.threadDoesNotExist(),uid)
    else:
        r = ""
    
        thread = c.threads.Collections.find_one({"id":int(n)})
        if thread:
            if admin(uid):
                r += html.delthread(thread["id"])
                return page(r,uid)
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.threadDoesNotExist(),uid)

@app.route("/delpost-<n>",methods=['GET','POST'])
def delpost(n):
    uid = getUID()

    if request.method == "POST":
        pid = int(request.form["pid"])
        post = c.posts.Collections.find_one({"id":pid})
        
        if post:
            if admin(uid) and getThread(post['tid'])['pid'] != post['id']:
                utils.delpost(pid)
                if "ajax" in request.form:
                    return "/thread-%d?type=4"%(post['tid'])
                else:
                    return redirect("/thread-%d?type=51"%(post['tid']))
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.postDoesNotExist(),uid)
    else:
        r = ""
    
        post = c.posts.Collections.find_one({"id":int(n)})
        if post:
            if admin(uid) and getThread(post['tid'])['pid'] != post['id']:
                r += html.delpost(post["id"])
                return page(r,uid)
            else:
                return page(html.permissionDenied(),uid)
        else:
            return page(html.postDoesNotExist(),uid)
        
@app.route("/hidepost-<n>")
def hidepost(n):
    uid = getUID()

    post = c.posts.Collections.find_one({"id":int(n)})
    if post:
        if admin(uid):
            utils.hidepost(post['id'])
            return redirect("thread-%d"%(post['tid']))
        else:
            return page(html.permissionDenied(),uid)
    else:
        return page(html.postDoesNotExist(),uid)

@app.route("/unhidepost-<n>")
def unhidepost(n):
    uid = getUID()

    post = c.posts.Collections.find_one({"id":int(n)})
    if post:
        if admin(uid):
            utils.unhidepost(post['id'])
            return redirect("thread-%d"%(post['tid']))
        else:
            return page(html.permissionDenied(),uid)
    else:
        return page(html.postDoesNotExist(),uid)

@app.route("/hidethread-<n>")
def hidethread(n):
    uid = getUID()

    thread = c.threads.Collections.find_one({"id":int(n)})
    if thread:
        if admin(uid):
            utils.hidethread(thread['id'])
            return redirect("thread-%d?type=2"%(thread['id']))
        else:
            return page(html.permissionDenied(),uid)
    else:
        return page(html.threadDoesNotExist(),uid)

@app.route("/unhidethread-<n>")
def unhidethread(n):
    uid = getUID()

    thread = c.threads.Collections.find_one({"id":int(n)})
    if thread:
        if admin(uid):
            utils.unhidethread(thread['id'])
            return redirect("thread-%d?type=3"%(thread['id']))
        else:
            return page(html.permissionDenied(),uid)
    else:
        return page(html.threadDoesNotExist(),uid)

@app.route("/lockthread-<n>")
def lockthread(n):
    uid = getUID()

    thread = c.threads.Collections.find_one({"id":int(n)})
    if thread:
        if admin(uid):
            utils.lockthread(thread['id'])
            return redirect("thread-%d?type=4"%(thread['id']))
        else:
            return page(html.permissionDenied(),uid)
    else:
        return page(html.threadDoesNotExist(),uid)

@app.route("/unlockthread-<n>")
def unlockthread(n):
    uid = getUID()

    thread = c.threads.Collections.find_one({"id":int(n)})
    if thread:
        if admin(uid):
            utils.unlockthread(thread['id'])
            return redirect("thread-%d?type=5"%(thread['id']))
        else:
            return page(html.permissionDenied(),uid)
    else:
        return page(html.threadDoesNotExist(),uid)

    
if __name__ == "__main__":
    app.run()

