from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash
from db import db

def get_restos():
    sql = "SELECT id, name, location, created_at FROM restos ORDER BY id DESC"
    result = db.session.execute(text(sql))
    restos = result.fetchall()
    return restos

def register_new(username, password):
    password_hash = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(text(sql), {"username":username, "password":password_hash})
        db.session.commit()
    except:
        return False
    return username, password

def fetch_user(username):
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    return result.fetchone()

def create_resto(name, location):
    sql = "INSERT INTO restos (name, location, created_at) VALUES (:name, :location, NOW()) RETURNING id"
    db.session.execute(text(sql), {"name":name, "location":location})
    db.session.commit()

def view_resto(id):
    sql = "SELECT name, location FROM restos WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    resto = result.fetchone()
    name = resto[0]
    location = resto[1]
    sql = "SELECT * FROM reviews WHERE resto_id=:id"
    result = db.session.execute(text(sql), {"id":id})
    reviews = result.fetchall()
    return [name, location, reviews]

def fetch_resto_name(id):
    sql = "SELECT name FROM restos WHERE id=:id"
    result = db.session.execute(text(sql), {"id":id})
    return result.fetchone()[0]

def create_review(id, content, username):
    sql = "INSERT INTO reviews (resto_id, content, sent_at, sent_by, visible) VALUES (:resto_id, :content, NOW(), :username, TRUE) RETURNING id"
    db.session.execute(text(sql), {"resto_id":id, "content":content, "username":username})
    db.session.commit()

def fetch_reviews(query):
    sql = "SELECT * FROM reviews JOIN restos ON reviews.resto_id = restos.id WHERE lower(content) LIKE lower(:query)"
    result = db.session.execute(text(sql), {"query":"%"+query+"%"})
    return result.fetchall()

def fetch_reviews_by_user(name):
    sql = "SELECT * FROM reviews WHERE reviews.sent_by=:username"
    result = db.session.execute(text(sql), {"username":name})
    return result.fetchall()

def delete_review(id):
    sql = "UPDATE reviews SET visible=FALSE WHERE reviews.id=:id"
    db.session.execute(text(sql), {"id":id})
    db.session.commit()
