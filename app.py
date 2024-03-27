from os import getenv
from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

@app.route("/")
def index():
    sql = "SELECT id, name, location, created_at FROM restos ORDER BY id DESC"
    result = db.session.execute(text(sql))
    restos = result.fetchall()
    return render_template("index.html", count=len(restos), restos=restos)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_new", methods=["POST"])
def register_new():
    username = request.form["username"]
    password = request.form["password"]
    password_again = request.form["password_again"]
    if password == password_again:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(text(sql), {"username":username, "password":hash_value})
        db.session.commit()
        return redirect("/")
    else:
        return redirect("/register")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    user = result.fetchone()
    if not user:
        return redirect(request.referrer)
    else:
        hash = user.password
        if check_password_hash(hash, password):
            session["username"] = username
            print(username)
        else:
            return redirect(request.referrer)
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/create", methods=["POST"])
def create():
    name = request.form["name"]
    location = request.form["location"]
    sql = "INSERT INTO restos (name, location, created_at) VALUES (:name, :location, NOW()) RETURNING id"
    result= db.session.execute(text(sql), {"name":name, "location":location})
    resto_id = result.fetchone()[0]

    db.session.commit()
    return redirect("/")

@app.route("/restaurant/<int:id>")
def restaurant(id):
    sql = "SELECT name, location FROM restos WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    resto = result.fetchone()
    name = resto[0]
    location = resto[1]
    sql = "SELECT * FROM reviews WHERE resto_id=:id"
    result = db.session.execute(text(sql), {"id":id})
    reviews = result.fetchall()
    return render_template("view_restaurant.html", id=id, name=name, location=location, reviews=reviews)

@app.route("/restaurant/<int:id>/review")
def review(id):
    sql = "SELECT name FROM restos WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    print(result)
    name = result.fetchone()[0]
    print(name)
    return render_template("review.html", id=id, name=name)

@app.route("/create_review/<int:id>", methods=["POST"])
def create_review(id):
    if session["username"]:
        content = request.form["content"]
        sql = "INSERT INTO reviews (resto_id, content, sent_at, sent_by, visible) VALUES (:resto_id, :content, NOW(), :username, TRUE) RETURNING id"
        result = db.session.execute(text(sql), {"resto_id":id, "content":content, "username":session["username"]})
        db.session.commit()
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
    reviews = []
    sql = "SELECT restos.name, resto_id, content FROM reviews JOIN restos ON reviews.resto_id = restos.id WHERE lower(content) LIKE lower(:query)"

    result = db.session.execute(text(sql), {"query":"%"+query+"%"})
    reviews = result.fetchall()
    return render_template("result.html", reviews=reviews)

@app.route("/personal")
def personal():
    sql = "SELECT * FROM reviews WHERE reviews.sent_by=:username"
    result = db.session.execute(text(sql), {"username":session["username"]})
    reviews = result.fetchall()
    return render_template("personal.html", reviews=reviews)

@app.route("/delete_review/<int:id>", methods=["POST"])
def delete_review(id):
    sql = "UPDATE reviews SET visible=FALSE WHERE reviews.id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()
    return redirect("/personal")