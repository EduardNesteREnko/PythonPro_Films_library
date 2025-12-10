import functools

from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
app = Flask(__name__)
app.secret_key = 'random string'

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

def decorator_check_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user_login'))
    #wrapper.__name__ = func.__name__
    return wrapper

@app.route("/")
@decorator_check_login
def main_page():
    with db_connection() as cur:
        result = cur.execute('SELECT * FROM film order by added_at desc limit 10').fetchall()
    #result = get_db_result("SELECT id, poster, name FROM film order by added_at desc limit 10")
    return render_template('main.html', films=result)


@app.route('/register', methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def user_register():
    with db_connection() as cur:
        first_name = request.form['fname']
        last_name = request.form['lname']
        password = request.form['password']
        login = request.form['login']
        email = request.form['email']
        birth_date = request.form['birth_date']
        cur.execute('INSERT INTO user (first_name, last_name, password, login, email, birth_date) VALUES (?, ?, ?, ?, ?, ?)',(first_name, last_name, password, login, email, birth_date))
    return render_template('register.html')


@app.route("/login", methods=["GET"])
def user_login():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def user_login_post():
     login = request.form['login']
     password = request.form['password']
     with db_connection() as cur:
         cur.execute('SELECT * FROM user where login= ? AND password = ?',(login, password))
         result = cur.fetchone()
     if result:
         session['logged_in'] = True
         session['user_id'] = result['id']
         return f'Login with user {result}'
     return 'Login failed'


@app.route("/logout", methods=["GET"])
@decorator_check_login
def user_logout():
    session.clear()
    return "Logout"

@app.route("/user/<user_id>", methods=["GET", "POST"])
@decorator_check_login
def user_profile(user_id):
    session_user_id = session.get('user_id')

    if request.method == "POST":

         if user_id == session_user_id:
             return "You can edit your profile"

         first_name = request.form['first_name']
         last_name = request.form['last_name']
         email = request.form['email']
         password = request.form['password']
         birth_date = request.form['birth_date']
         phone = request.form['phone']
         photo = request.form['photo']
         additional_info = request.form['additional_info']
         with db_connection() as cur:
             cur.execute(f'UPDATE user SET first_name ="{first_name}", last_name="{last_name}", email="{email}", password="{password}", birth_date="{birth_date}", phone_number="{phone}", additional_info="{additional_info}" WHERE id={user_id} ')
             result = cur.fetchone()
             return 'User profile updated'
             #return render_template("user_profile.html", user_id=user_id)
    else:
        with db_connection() as cur:
            cur.execute(f'SELECT * FROM user WHERE id={user_id}')
            user_by_id = cur.fetchone()

            if session_user_id is None:
                user_by_session = 'No user in session'
            else:
                cur.execute(f'SELECT * FROM user WHERE id={session_user_id}')
                user_by_session = cur.fetchone()
        return render_template('user_page.html', user = user_by_id, user_session=user_by_session)
        #return f'You`ve logged in as {user_by_session}'


@app.route("/user/<user_id>/delete", methods=["GET"])
@decorator_check_login
def user_delete(user_id):
    session_user_id = session.get('user_id')
    if user_id == session_user_id:
        return f"User {user_id} deleted"
    else:
        return f"You can delete only your profile"

@app.route("/films", methods=["GET"])
def films():
    filter_params = request.args
    filter_list_texts = []
    for key, value in filter_params.items():
        if value:
            if key == 'name':
                filter_list_texts.append(f'name like "%{value}%"')
            else:
                filter_list_texts.append(f'{key}="{value}"')
    additional_filter = ""
    if filter_params:
        additional_filter =  " WHERE " + " AND ".join(filter_list_texts)
    result = get_db_result(f'SELECT * FROM film {additional_filter} order by added_at desc')
    #result = get_db_result("SELECT id, poster, name FROM film order by added_at desc")
    countries = get_db_result('SELECT * FROM country')
    return render_template('films.html', films=result, countries = countries)

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


