from flask import redirect, render_template, abort, request, session
from werkzeug.security import check_password_hash
from secrets import token_hex
from app import app
import visits


def check_user():
    if session["csrf_token"] != request.form["csrf_token"]:
        return abort(403)
    
def clear_error_messages():
    session["passwords_differ"] = False
    session["username_in_use"] = False
    session["registration_successful"] = False

@app.route("/")
def index():
    clear_error_messages()
    restos = visits.get_restos()
    return render_template("index.html", count=len(restos), restos=restos)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_again = request.form["password_again"]
        if password != password_again:
            session["passwords_differ"] = True
            return redirect("/register")
        if visits.register_new(username, password):
            clear_error_messages()
            session["registration_successful"] = True
            return redirect("/")
        elif not visits.register_new(username, password):
            session["username_in_use"] = True
            return redirect("/register")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = visits.fetch_user(username)

    if not user:
        session["invalid_user"] = True
        return redirect(request.referrer)
    else:
        hash = user.password
        if check_password_hash(hash, password):
            session["username"] = username
            session["invalid_user"] = False
            session["csrf_token"] = token_hex(16)
        else:
            session["invalid_user"] = True
            return redirect(request.referrer)
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    del session["username"]
    del session["invalid_user"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/create", methods=["POST"])
def create():
    name = request.form["name"]
    location = request.form["location"]
    visits.create_resto(name, location)
    check_user()
    return redirect("/")

@app.route("/restaurant/<int:id>")
def restaurant(id):
    resto = visits.view_resto(id)
    name = resto[0]
    location = resto[1]
    reviews = resto[2]
    return render_template("view_restaurant.html", id=id, name=name, location=location, reviews=reviews)

@app.route("/restaurant/<int:id>/review")
def review(id):
    name = visits.fetch_resto_name(id)
    return render_template("review.html", id=id, name=name)

@app.route("/create_review/<int:id>", methods=["POST"])
def create_review(id):
    if session["username"]:
        visits.create_review(id, request.form["content"], session["username"])
    check_user()
    return redirect(f"/restaurant/{id}")

@app.route("/result")
def result():
    query = request.args["query"]
    reviews = visits.fetch_reviews(query)
    return render_template("result.html", reviews=reviews)

@app.route("/personal")
def personal():
    reviews = visits.fetch_reviews_by_user(session["username"])
    visible = False
    for review in reviews:
        if review.visible == True:
            visible = True
            break
    return render_template("personal.html", reviews=reviews, visible=visible)

@app.route("/delete_review/<int:id>", methods=["POST"])
def delete_review(id):
    visits.delete_review(id)
    print(id)
    return redirect("/personal")
