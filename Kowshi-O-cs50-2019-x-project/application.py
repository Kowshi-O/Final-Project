import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///home.db")


@app.route("/")
@login_required
def index():
    """homepage"""
    return redirect("/viewtodo")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow user to change their password"""

    if request.method == "POST":

        # Ensure current password is not empty
        if not request.form.get("current_password"):
            return apology("must provide current password", 400)

        # Query database for user_id
        rows = db.execute("SELECT hash FROM users WHERE id = :user_id", user_id=session["user_id"])

        # Ensure current password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
            return apology("invalid password", 400)

        # Ensure new password is not empty
        if not request.form.get("new_password"):
            return apology("must provide new password", 400)

        # Ensure new password confirmation is not empty
        elif not request.form.get("new_password_confirmation"):
            return apology("must provide new password confirmation", 400)

        # Ensure new password and confirmation match
        elif request.form.get("new_password") != request.form.get("new_password_confirmation"):
            return apology("new password and confirmation must match", 400)

        # Update database
        hash = generate_password_hash(request.form.get("new_password"))
        rows = db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", user_id=session["user_id"], hash=hash)

        # Show flash
        flash("Changed!")

    return render_template("change_password.html")

@app.route("/delete", methods=["GET","POST"])
@login_required
def delete():

   if request.method == "POST":

       if not request.form.get("delkey"):
           return apology("Must Provide Valid Key.")

       delete = db.execute("DELETE FROM todolist WHERE IDENT = :delkey AND id = :id", delkey=request.form.get("delkey"), id=session["user_id"])
       return redirect("/viewtodo")

   else:
       return render_template("compete.html")


@app.route("/deleteA", methods=["GET","POST"])
@login_required
def deleteA():

   if request.method == "POST":

       if not request.form.get("appdel"):
           return apology("Must Provide Valid Key.")

       delete = db.execute("DELETE FROM appointments WHERE IDENT = :appdel AND id = :id", appdel=request.form.get("appdel"), id=session["user_id"])
       return redirect("/viewtodo")

   else:
       return render_template("compete.html")






@app.route("/tick", methods=["GET","POST"])
@login_required
def tick():
   if request.method == "POST":
        comp = db.execute("UPDATE todolist SET compYN = 'Yes!' WHERE ident = :compkey AND id = :id", compkey=request.form.get("compkey"), id=session["user_id"])
        return redirect("/complete")

   else:
       return render_template("compete.html")

@app.route("/compete", methods=["GET", "POST"])
@login_required
def alter():
    return render_template("compete.html")


@app.route("/complete", methods=["GET","POST"])
@login_required
def complete():

        completed = db.execute("SELECT id, task, duedate, taskType, createdOn, compYN, IDENT FROM todolist WHERE compYN = 'Yes!' AND id = :id ", id=session["user_id"])
        return render_template("completed.html", completed=completed)



@app.route("/todo", methods=["GET","POST"])
@login_required
def todo():
    if request.method == "POST":
        # Ensure task was submitted
        if not request.form.get("task"):
            return apology("must provide task", 400)

        # Insert task into database
        todo = db.execute("INSERT INTO todolist (id, task, duedate, taskType) VALUES(:id, :task, :due, :taskType)", taskType=request.form.get("type"), id=session["user_id"], task=request.form.get("task"), due=request.form.get("due"))

        return redirect("/viewtodo")


        # If user already exists return apology
        if not todo:
            return apology("not working", 400)


    else:
        return render_template("todo.html")

@app.route("/appointment", methods=["GET","POST"])
@login_required
def appoint():
    if request.method == "POST":
        # Ensure task was submitted
        if not request.form.get("placeA"):
            return apology("must provide place", 400)

        # Insert task into database
        appt = db.execute("INSERT INTO appointments (id, place, date, time) VALUES(:id, :place, :date, :time)", place=request.form.get("placeA"), id=session["user_id"], date=request.form.get("dateA"), time=request.form.get("timeA"))

        return redirect("/viewtodo")


        # If user already exists return apology
        if not todo:
            return apology("not working", 400)


    else:
        return render_template("todo.html")


@app.route("/viewtodo")
@login_required
def viewTodo():

    taskss = db.execute("SELECT id, task, duedate, taskType, createdOn, ident, compYN FROM todolist WHERE id = :id", id=session["user_id"])
    appts = db.execute("SELECT id, place, date, time, ident FROM appointments WHERE id = :id", id=session["user_id"])
    return render_template("view.html", taskss=taskss, appts=appts)


@app.route("/about")
def about():
    """aboutPage"""
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/about")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords must match", 400)


        # Encrypt password
        hash = generate_password_hash(request.form.get("password"))

        # Insert user into database
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash=hash)
        # If user already exists return apology
        if not result:
            return apology("Username already exists", 400)


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return render_template("login.html")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
