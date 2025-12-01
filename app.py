from flask import Flask, render_template, request
import sqlite3
app = Flask(__name__)

def film_dictionary(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        return d

class db_connection:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.conn.row_factory = film_dictionary
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

def get_db_result(query):
    con = sqlite3.connect('database.db')
    con.row_factory = film_dictionary
    cur = con.cursor()
    res = cur.execute(query)
    result = res.fetchall()
    con.close()
    return result

@app.route("/")
def main_page():
    with db_connection() as cur:
        result = cur.execute('SELECT * FROM film order by added_at desc limit 10').fetchall()
    #result = get_db_result("SELECT id, poster, name FROM film order by added_at desc limit 10")
    return result


@app.route('/register', methods=["GET"])
def register_page():
    return """
    <form action="/register" method="POST">

    <label for="fname">First name:</label><br>
    <input type="text" id="fname" name="fname" value="John"><br><br>
    
    <label for="lname">Last name:</label><br>
    <input type="text" id="lname" name="lname"><br>
    
    <label for="password">password:</label><br>
    <input type="password" id="password" name="password"><br>
    
    <label for="email">email:</label><br>
    <input type="email" id="email" name="email"><br>
    
    <label for="login">login:</label><br>
    <input type="text" id="login" name="login"><br>
    
    <label for="birth_date">birth_date:</label><br>
    <input type="date" id="birth_date" name="birth_date"><br>

    <input type="submit" value="Submit">
    </form>
    """

@app.route("/register", methods=["POST"])
def user_register():
    with db_connection() as cur:
        first_name = request.form['fname']
        last_name = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        login = request.form['login']
        birth_date = request.form['birth_date']
        cur.execute('INSERT INTO user (first_name, last_name, email, password, login, birth_date) VALUES (?, ?, ?, ?, ?, ?)',(first_name, last_name, email, password, login, birth_date))
    return 'Registered'
    #return render_template('register.html')


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
    result = get_db_result("SELECT id, poster, name FROM film order by added_at desc")
    return result

@app.route("/films", methods=["POST"])
def film_add():
    return f"Film added"

@app.route("/films/<film_id>", methods=["GET"])
def film_info(film_id):
    with db_connection() as cur:
        result = cur.execute(f"SELECT * FROM film where id={film_id}").fetchall()
        actors = cur.execute(f"SELECT * FROM actor join actor_film on actor.id == actor_film.actor_id where actor_film.film_id={film_id}").fetchall()
        genre = cur.execute(f'SELECT * FROM genre_film where film_id={film_id} ').fetchall()
    #result = get_db_result(f"SELECT * FROM film where id={film_id}")
    #actors = get_db_result(f"SELECT * FROM actor join actor_film on actor.id == actor_film.actor_id where actor_film.film_id={film_id}")
    #genre = get_db_result(f'SELECT * FROM genre_film where film_id={film_id} ')
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


