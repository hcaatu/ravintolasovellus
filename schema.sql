CREATE TABLE restos (id SERIAL PRIMARY KEY, name TEXT, location TEXT, created_at TIMESTAMP);
CREATE TABLE reviews (id SERIAL PRIMARY KEY, resto_id INT, content TEXT, sent_at TIMESTAMP, sent_by TEXT, visible BOOLEAN);
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT);
CREATE TABLE friends (id SERIAL PRIMARY KEY, user1_id INT, user2_id INT, accepted BOOLEAN, visible BOOLEAN);
