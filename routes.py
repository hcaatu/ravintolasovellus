from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
import visits

@app.route("/")
def index():
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
            return redirect("/")
        # todo error message
        if visits.register_new(username, password):
            return redirect("/")
        else:
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
        else:
            session["invalid_user"] = True
            return redirect(request.referrer)
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    del session["username"]
    del session["invalid_user"]
    return redirect("/")

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/create", methods=["POST"])
def create():
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
    return render_template("view_restaurant.html", id=id, name=name, location=location, reviews=reviews)

@app.route("/restaurant/<int:id>/review")
def review(id):
    name = visits.fetch_resto_name(id)
    return render_template("review.html", id=id, name=name)

@app.route("/create_review/<int:id>", methods=["POST"])
def create_review(id):
    if session["username"]:
        visits.create_review(id, request.form["content"], session["username"])
    return redirect(f"/restaurant/{id}")

@app.route("/result")
def result():
    """Handles the search result content page.

    Uses the built-in lower-fuction to work as a case insensitive search.
    Joins the restaurant name using the id found in the review table.

    Returns:
        str: The rendered html page with searched results.
    """
    query = request.args["query"]
    reviews = visits.fetch_reviews(query)
    print(reviews)
    return render_template("result.html", reviews=reviews)

@app.route("/personal")
def personal():
    reviews = visits.fetch_reviews_by_user(session["username"])
    print(reviews)
    return render_template("personal.html", reviews=reviews)

@app.route("/delete_review/<int:id>", methods=["POST"])
def delete_review(id):
    visits.delete_review(id)
    return redirect("/personal")
