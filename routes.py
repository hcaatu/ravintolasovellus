from flask import redirect, render_template, abort, request, session
from werkzeug.security import check_password_hash
from secrets import token_hex
from app import app
import visits


def check_user():
    try:
        if session["csrf_token"] != request.form["csrf_token"]:
            return abort(403)
    except KeyError:
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
            session["user_id"] = user.id
            session["username"] = username
            session["invalid_user"] = False
            session["csrf_token"] = token_hex(16)
        else:
            session["invalid_user"] = True
            return redirect(request.referrer)
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    del session["invalid_user"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/create", methods=["POST"])
def create():
    check_user()
    name = request.form["name"]
    location = request.form["location"]
    visits.create_resto(name, location)
    return redirect("/")

@app.route("/restaurant/<int:id>")
def restaurant(id):
    resto = visits.view_resto(id)
    name = resto[0]
    location = resto[1]
    reviews = resto[2]
    google_location = str(location).replace(" ", "+")
    return render_template("view_restaurant.html", id=id, name=name, location=location, reviews=reviews, google_location=google_location)

@app.route("/restaurant/<int:id>/review")
def review(id):
    name = visits.fetch_resto_name(id)
    return render_template("review.html", id=id, name=name)

@app.route("/create_review/<int:id>", methods=["POST"])
def create_review(id):
    check_user()
    if session["username"]:
        visits.create_review(id, request.form["content"], session["username"])
    return redirect(f"/restaurant/{id}")

@app.route("/result")
def result():
    query = request.args["query"]
    reviews = visits.fetch_reviews(query)
    return render_template("result.html", reviews=reviews)

@app.route("/personal")
def personal(id=None):
    friends = visits.fetch_friends_by_user(session["user_id"])
    reviews = visits.fetch_reviews_by_user(session["username"])
    print(friends)
    visible = False
    for review in reviews:
        if review.visible == True:
            visible = True
            break
    return render_template("personal.html", friends=friends, reviews=reviews, visible=visible)

@app.route("/delete_review/<int:id>", methods=["POST"])
def delete_review(id):
    visits.delete_review(id)
    print(id)
    return redirect("/personal")

@app.route("/users", methods=["GET"])
def users():
    #check_user()
    if request.method == "GET":
        query = request.args["query"]
        users = visits.get_users_by_query(query)
        print(users)
        for user in users:
            print(user)
        return render_template("users.html", users=users)
    
@app.route("/users/<int:id>", methods=["POST"])
def friend_request(id):
    print("aa")
    print(id)
    print(session["user_id"])
    check_user()
    visits.add_friend_request(session["user_id"], id)
    return redirect("/")

@app.route("/accept_friend/<int:id>", methods=["POST"])
def accept_friend(id):
    print(id)
    check_user()
    visits.accept_friend(id)
    return redirect("/personal")