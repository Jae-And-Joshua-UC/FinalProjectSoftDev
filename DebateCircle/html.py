import cgi

import utils
import app
from utils import getUser, getThread, getForum, getPost, admin
# THIS FILE
# converts python code to HTML


DATE_FORMAT = "%b %d %Y, %I:%M:%S%p"

def getHeader(uid):
    if uid == -1:
        return '''
<nav class="navbar navbar-default">
<div class="navbar-header">
<a class="navbar-brand" href="/">Home</a>
<ul class="nav navbar-nav">
<li class="active"><a href="login">Login</a></li>
<li><a href="register">Register</a></li>
</ul>

</div>
</nav>
'''
    else:
        return '''
<nav class="navbar navbar-default">
<div class="navbar-header">
<a class="navbar-brand" href="/">Home</a>
<p class="navbar-text">Logged in as <strong>%s</strong></p>
<ul class="nav navbar-nav">
<li><a href="logout">Logout</a></li>
</ul>

</div>
</nav>
'''%(getUser(uid)["username"])



def pager(ra,cur,url):
    r = ""
    for x in range(ra[0],ra[1]):
        if x == cur:
            r += '<li class="active"><a href="%s%d">%d</a></li>'%(url,x,x)
        else:
            r += '<li><a href="%s%d">%d</a></li>'%(url,x,x)
    return r

def pages(cur,mx,url):
    chooser = '<li><a href="javascript:void(0)" class="pgchooser">...</a></li>'
    r = '<ul class="pagination">'
    if cur == 1:
        r += """
<li class="disabled"><a href="%s1">&laquo;</a></li>
<li class="active"><a href="%s1">1</a></li>
"""%(url,url)
    else:
        r += """
<li><a href="%s1">&laquo;</a></li>
<li><a href="%s1">1</a></li>
"""%(url,url)

    if cur <= 4:
        r += pager([2,min(cur+2,mx)],cur,url)
        if mx-cur == 3:
            r += pager([cur+2,cur+3],cur,url)
        if mx-cur > 3:
            r += chooser
    elif mx-cur < 4:
        r += chooser
        r += pager([cur-1,mx],cur,url)
    else:
        r += chooser
        r += pager([cur-1,cur+2],cur,url)
        r += chooser




    if cur == mx:
        if cur != 1:
            r += '<li class="active"><a href="%s%d">%d</a></li>'%(url,mx,mx)
        r += '<li class="disabled"><a href="%s%d">&raquo;</a></li>'%(url,mx)
    else:
        r += """
<li><a href="%s%d">%d</a></li>
<li><a href="%s%d">&raquo;</a></li>
"""%(url,mx,mx,url,mx)

        

 
 


    r += '</ul>'

    return r



def forum(n):
    r = """
<tr class="active">
<td class="f_name"><a href="forum-%(id)d">%(name)s</a><div class="desc">%(desc)s</a></div></td>"""%(n)
    r += '<td class="f_num">%d</td><td class="f_num">%d</td>'%(utils.forumThreadCount(n['id']),utils.forumPostCount(n['id']))

    a = utils.lastPostInfoForum(n['id'])
    if a:
        r += '<td class="f_last"><a href="thread-%d">%s</a> by <a href="user-%d">%s</a><br />%s</td>'%(a['tid'], a['title'], a['uid'],a['username'],a['date'].strftime(DATE_FORMAT))
    else:
        r += '<td class="f_last">No threads</td>'
    return r

def thread(n,admin):
    r = ""
    if n['hid']:
        r += '<tr class="danger">'
        if not admin:
            r += '<td colspan="4">This thread has been hidden by an administrator.</td></tr>'
            return r
    elif n['lock']:
        r += '<tr class="warning">'
    else:
        r += '<tr class="active">'
    r += '<td class="t_name">'

    if "lock" in n.keys() and n['lock']:
        r += '<span class="glyphicon glyphicon-lock"></span> '

    r += '<a href="thread-%(id)d">%(title)s</a><div class="desc">%(desc)s</a></div></td>'%(n)
    r += '<td class="t_author"><a href="user-%(id)d">%(username)s</a></td>'%(getUser(n['uid']))
    r += '<td class="t_num">%d</td>'%(utils.threadPostCount(n['id']))
    
    a = utils.lastPostInfo(n['id'])
    r += '<td class="t_last"><a href="user-%d">%s</a><br />%s</td>'%(a['uid'],a['username'],a['date'].strftime(DATE_FORMAT))
    r += '</tr>'
    return r

def post(uid,n):
    user = getUser(n["uid"])
    thread = getThread(n['tid'])
    n["username"] = user["username"]
    n["date"] = n["date"].strftime(DATE_FORMAT)

    n['className'] = "active"
    show = True
    if not n['hid'] or admin(uid):
        n["content"] = "<br />".join(cgi.escape(n["content"]).split("\n"))
    else:
        show = False
        n["content"] = "This post has been hidden by an administrator."
    if n['hid']:
        n['className'] = "danger"

    # allow editing abilities
    n['pleft'] = ""
    if uid == n["uid"] or admin(uid):
        n['pleft'] = '<a href="/editpost-%d" class="btn btn-primary">Edit</a>'%(n['id'])

    # admin buttons
    if admin(uid):
        # if it isn't the first post

         #   n['pleft'] += ' &nbsp; <a href="/delpost-%d" class="btn btn-danger">Delete</a>'%(n['id'])
#            n['pleft'] += '<br /><br /><a href="#">Hide</a> &nbsp; &nbsp; <a href="#">Delete</a>'
        if n['hid']:
            n['pleft'] += ' <a href="unhidepost-%d" class="btn btn-warning">Unhide</a>'%(n['id'])
        else:
            n['pleft'] += ' <a href="hidepost-%d" class="btn btn-warning">Hide</a>'%(n['id'])
        if n['id'] != thread['pid']:
            n['pleft'] += ' <a href="/delpost-%d" class="btn btn-danger deletePost">Delete</a>'%(n['id'])


    # show last post edit time
    if "editdate" in n.keys():
        n['editdate'] = " - Lasted edited on %s"%(n["editdate"].strftime(DATE_FORMAT))
        if n["edituid"] != n["uid"]:
            n['editdate'] += " by <strong>%s</strong>"%(getUser(n['edituid'])['username'])
    else:
        n['editdate'] = ""

    r = """
<table class="table p_post" cellspacing="0">
<tr class="%(className)s">
<td class="p_left">"""%(n)
    if show:
        r += '<div class="user"><a href="user/%(uid)d">%(username)s</a></div><div class="p_buttons">%(pleft)s</div>'%(n)
    r += """</td>
<td class="p_right"><div class="p_date">%(date)s %(editdate)s</div><div class="p_content">%(content)s</div></td>
</tr>
</table>"""%(n)
    

    return r




# CREATE NEW ...
# add post, n = tid
def reply(n):
    thread = getThread(n)
    forum = getForum(thread["fid"])
    nav = utils.nav([
            ["/",app.getFn()],
            ["/forum-%d"%(forum['id']),forum["name"]],
            ["thread-%d"%(thread['id']),thread["title"]],
            ["Reply"]
            ])

    r = """
<div id="header">Reply</div>%s
<form method="post">
<input type="hidden" name="tid" value="%d" />
<table class="table">
<tr class="active"><td><textarea name="content" class="form-control" rows="12" placeholder="Enter your post here..."></textarea></td></tr>
<tr class="active"><td style="text-align:center;">
  <input type="submit" class="btn btn-primary" value="Reply" name="reply" />
  <input type="submit" class="btn btn-primary" value="Cancel" name="cancel" />
</td></tr>
</table>
</form>%s"""%(nav,n,nav)
    return r

# new thread, n = fid
def newthread(n):
    forum = getForum(n)
    nav = utils.nav([
            ["/",app.getFn()],
            ["/forum-%d"%(forum['id']),forum["name"]],
            ["Create New Thread"]
            ])

    r = """
<div id="header">Create New Thread</div>%s
<form method="post">
<input type="hidden" name="fid" value="%d" />
<table class="table">
<tr class="active"><td><div class="col-xs-3"><input name="title" type="text" class="form-control" placeholder="Enter your title here..."  /></div></td></tr>
<tr class="active"><td><div class="col-xs-8"><input name="desc" type="text" class="form-control" placeholder="Enter a description here... (Optional)"  /></div></td></tr>
<tr class="active"><td><textarea name="content" class="form-control" rows="12" placeholder="Enter your post here..."></textarea></td></tr>
<tr class="active"><td style="text-align:center;">
  <input type="submit" class="btn btn-primary" value="Create Thread" name="reply" />
  <input type="submit" class="btn btn-primary" value="Cancel" name="cancel" />
</td></tr>
</table>
</form>%s"""%(nav,n,nav)
    return r

    
def editpost(n):
    post = getPost(n)
    thread = getThread(post["tid"])
    forum = getForum(thread["fid"])
    nav = utils.nav([
            ["/",app.getFn()],
            ["/forum-%d"%(forum['id']),forum["name"]],
            ["thread-%d"%(thread['id']),thread["title"]],
            ["Edit Post"]
            ])

    r = """
<div id="header">Edit Post</div>%s
<form method="post">
<input type="hidden" name="pid" value="%d" />
<table class="table">
<tr class="active"><td><textarea name="content" class="form-control" rows="12" placeholder="Enter your post here...">%s</textarea></td></tr>
<tr class="active"><td style="text-align:center;">
  <input type="submit" class="btn btn-primary" value="Edit Post" name="reply" />
  <a class="btn btn-primary" href="thread-%d">Cancel</a>
</td></tr>
</table>
</form>%s"""%(nav,n,cgi.escape(post["content"]),n,nav)
    return r

def edittitle(n):
    thread = getThread(n)
    forum = getForum(thread["fid"])
    nav = utils.nav([
            ["/",app.getFn()],
            ["/forum-%d"%(forum['id']),forum["name"]],
            ["thread-%d"%(thread['id']),thread["title"]],
            ["Edit Thread Title"]
            ])

    r = """
<div id="header">Edit Thread Title</div>%s
<form method="post">
<input type="hidden" name="tid" value="%d" />
<table class="table">
<tr class="active"><td><div class="col-xs-3"><input name="title" type="text" class="form-control" placeholder="Enter your title here..." value="%s" /></div></td></tr>
<tr class="active"><td><div class="col-xs-8"><input name="desc" type="text" class="form-control" placeholder="Enter a description here... (Optional)" value="%s" /></div></td></tr>
<tr class="active"><td>
  <input type="submit" class="btn btn-primary" value="Edit Title" name="reply" />
  <a class="btn btn-primary" href="thread-%d">Cancel</a>
</td></tr>
</table>
</form>%s"""%(nav,n,cgi.escape(thread["title"]),cgi.escape(thread["desc"]),n,nav)
    return r



def delthread(n):
    thread = getThread(n)
    forum = getForum(thread["fid"])
    nav = utils.nav([
            ["/",app.getFn()],
            ["/forum-%d"%(forum['id']),forum["name"]],
            ["thread-%d"%(thread['id']),thread["title"]],
            ["Delete Thread"]
            ])

    r = """
<div id="header">Are you sure you wish to delete this thread?</div>%s
<form method="post">
<input type="hidden" name="tid" value="%d" />
<div style="text-align:center">
<input type="submit" value="Yes, delete this thread" class="btn btn-danger" name="del" />
<br /><br /><a href="thread-%d">No, take me back to the thread</a>
</div>
</form>%s"""%(nav,n,n,nav)
    return r

def delpost(n):
    post = getPost(n)
    thread = getThread(post['tid'])
    forum = getForum(thread["fid"])
    nav = utils.nav([
            ["/",app.getFn()],
            ["/forum-%d"%(forum['id']),forum["name"]],
            ["thread-%d"%(thread['id']),thread["title"]],
            ["Delete Post"]
            ])

    r = """
<div id="header">Are you sure you wish to delete this post?</div>%s
<form method="post">
<input type="hidden" name="pid" value="%d" />
<div style="text-align:center">
<input type="submit" value="Yes, delete this post" class="btn btn-danger" name="del" />
<br /><br /><a href="thread-%d">No, take me back to the thread</a>
</div>
</form>%s"""%(nav,n,thread['id'],nav)
    return r






def login(n):
    nav = utils.nav([["/",app.getFn()],["Login"]])

    er = ""
    if n:
        if n == 1:
            erno = "Username/password combination does not exist"
        er = '<div class="alert alert-danger"><strong>Error:</strong> %s</div>'%(erno)

    return """
<div id="header">Login</div>%s
<div style="width:300px;margin-left:auto;margin-right:auto;">
%s
<form method="post">
<table class="table">
<tr class="active"><td><input tabindex="1" name="username" type="text" class="form-control" placeholder="Username" /></td></tr>
<tr class="active"><td><input tabindex="2" name="password" type="password" class="form-control" placeholder="Password" /></td></tr>
<tr class="active"><td style="text-align:center">Don't have an account?  Register an account by clicking <a href="register">here</a></td></tr>
<tr class="active"><td style="text-align:center"><input tabindex="3" type="submit" class="btn btn-primary" value="Login" /></td></tr>
</table>
</form>
</div>%s"""%(nav,er,nav)

def register(n):
    nav = utils.nav([["/",app.getFn()],["Register"]])

    er = ""
    if n:
        if n == 1:
            erno = "Username already in use"
        elif erno == 2:
            erno = "Passwords don't match"
        er = '<div class="alert alert-danger"><strong>Error:</strong> %s</div>'%(erno)

    return """
<div id="header">Register</div>%s
<div style="width:300px;margin-left:auto;margin-right:auto;">
%s
<form method="post">
<table class="table">
<tr class="active"><td><input tabindex="1" name="username" type="text" class="form-control" placeholder="Username" /></td></tr>
<tr class="active"><td><input tabindex="2" name="password" type="password" class="form-control" placeholder="Password" /></td></tr>
<tr class="active"><td><input tabindex="3" name="password2" type="password" class="form-control" placeholder="Confirm Password" /></td></tr>
<tr class="active"><td style="text-align:center">Already have an account?  Login by clicking <a href="login">here</a></td></tr>
<tr class="active"><td style="text-align:center"><input tabindex="4" type="submit" class="btn btn-primary" value="Register" /></td></tr>
</table>
</form>
</div>%s"""%(nav,er,nav)



def permissionDenied():
    return """
<div class="alert alert-danger"><strong>Error:</strong> You do not have permission to do this action.</div>
<div class="alert alert-info" style="text-align:center"><a href="/">Back to Index Page</a></div>"""

def postDoesNotExist():
    return """
<div class="alert alert-danger"><strong>Error:</strong> Post does not exist.</div>
<div class="alert alert-info" style="text-align:center"><a href="/">Back to Index Page</a></div>"""
def threadDoesNotExist():
    return """
<div class="alert alert-danger"><strong>Error:</strong> Thread does not exist.</div>
<div class="alert alert-info" style="text-align:center"><a href="/">Back to Index Page</a></div>"""
