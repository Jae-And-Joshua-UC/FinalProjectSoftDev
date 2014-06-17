from flask import Flask
from flask import render_template, session, redirect, url_for, request
import auth

app = Flask(__name__)
app.debug = True
app.secret_key = "joshandjae"

@app.route("/")
def index():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect(url_for("login"))
    
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if auth.authorize(str(request.form["username"]), str(request.form["password"])):
            session["username"] = request.form["username"]
            session["password"] = request.form["password"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html",type=1)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.pop("username",None)

    return redirect(url_for("index"))
@app.route("/register", methods=["GET","POST"])

def register():
    if request.method == "POST":
        if request.form["password"] == request.form["password2"]:
            if auth.createUser(str(request.form["username"]),str(request.form["password"])):
                return redirect(url_for("login"))
            else:
                return render_template("register.html",type=1)
    else:
        return render_template("register.html")
if __name__ == "__main__":
    app.run()
