from flask import Flask, render_template, request
import sqlite3
app = Flask(__name__)

@app.route("/")
def main_page():

    con = sqlite3.connect('database.db')
    cur = con.cursor()
    res = cur.execute("SELECT id, poster, name FROM film order by added_at desc limit 10")
    result = res.fetchall()
    con.close()
    return str(result)

@app.route("/register", methods=["POST"])
def user_register():
    return render_template("register.html")

@app.post("/login")
def user_login():
    return render_template('login.html')

@app.route("/logout", methods=["GET"])
def user_logout():
    return "Logout"

@app.route("/user/<user_id>", methods=["GET", "PATCH"])
def user_profile(user_id):
    return f"User {user_id}"

@app.route("/user/<user_id>", methods=["DELETE"])
def user_delete(user_id):
    return f"User {user_id} deleted"

@app.route("/films", methods=["GET"])
def films():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    res = cur.execute("SELECT id, poster, name FROM film order by added_at desc")
    result = res.fetchall()
    return result

@app.route("/films", methods=["POST"])
def film_add():
    return f"Film added"

@app.route("/films/<film_id>", methods=["GET"])
def film_info(film_id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM film where id={film_id}")
    result = res.fetchone()

    actors = cur.execute(f"SELECT * FROM actor join actor_film on actor.id == actor_film.actor_id where actor_film.film_id={film_id}").fetchall()
    genre = cur.execute(f'SELECT * FROM genre_film where film_id={film_id} ').fetchall()
    return f"Film {film_id} is {result}, actors {actors}, genres {genre}"

@app.route("/films/<film_id>", methods=["DELETE"])
def film_delete(film_id):
    return f"Film {film_id} deleted"

@app.route("/films/<film_id>", methods=["PATCH"])
def film_update(film_id):
    return f"Film {film_id} updated"


@app.route("/films/<film_id>/rating", methods=["POST"])
def film_rating (film_id):
    return f"Film {film_id} rated"

@app.route("/films/<film_id>/rating", methods=["GET"])
def film_rating_info(film_id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM feedback where film_id={film_id}')
    result = cur.fetchall()
    con.close()
    return f"Film rating {film_id} is {result}"


@app.route("/films/<film_id>/rating/<feedback_id>", methods=["PUT"])
def film_rating_update(film_id, feedback_id):
    return f"Film {film_id} rating updated {feedback_id}"

@app.route("/films/<film_id>/rating/<feedback_id>", methods=["DELETE"])
def film_rating_deletee(film_id, feedback_id):
    return f"Film {film_id} feedback {feedback_id} deleted"

@app.route("/films/<film_id>/rating/<feedback_id>/feedback", methods=["GET"])
def film_rating_feedback(film_id, feedback_id):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM feedback where film_id={film_id} and feedback_id={feedback_id}')
    result = cur.fetchall()
    con.close()
    return f"Film {film_id} rating {feedback_id} feedback, result is {result}"

@app.route("/user/<user_id>/list", methods=["GET", "POST"])
def user_lists(user_id):
    return f"Lists of {user_id}"

@app.route("/user/<user_id>/list", methods=["DELETE"])
def user_lists_delete(user_id):
    return f"List {user_id} deleted"

@app.route("/user/<user_id>/list/<list_id>", methods=["GET", "POST"])
def user_lists_info(user_id, list_id):
    return f"User {user_id} list item {list_id}"

@app.route("/user/<user_id>/list/<list_id>/<film_id>", methods=["DELETE"])
def user_list_item_delete( user_id, list_id, film_id):
    return f"User {user_id} list item {list_id}, film {film_id}deleted"


if __name__ == '__main__':
    app.run(debug=True)


