import functools
import select
from dateutil import parser, relativedelta
from sqlalchemy import select, update, func
from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import sqlite3
import os
import database
import models

app = Flask(__name__)
app.secret_key = 'random string'


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

    database.init_db()
    smth = select(models.Film).limit(10).order_by(models.Film.added_at.desc())
    data = database.db_session.execute(smth).fetchall()
    data2 = [itm[0] for itm in data]
    return render_template('main.html', films=data2)


@app.route('/register', methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def user_register():
    first_name = request.form['fname']
    last_name = request.form['lname']
    password = request.form['password']
    login = request.form['login']
    email = request.form['email']
    birth_date = parser.parse(request.form['birth_date'])
    database.init_db()

    new_user = models.User(first_name=first_name, last_name=last_name, email=email, password=password, login = login, birth_date=birth_date)
    database.db_session.add(new_user)
    database.db_session.commit()

    return render_template('register.html')


@app.route("/login", methods=["GET"])
def user_login():
    return render_template('login.html')

@app.route("/login", methods=["POST"])
def user_login_post():
     login = request.form['login']
     password = request.form['password']

     database.init_db()

     stmt = select(models.User).where(models.User.login == login, models.User.password == password)
     data = database.db_session.execute(stmt).fetchall()

     result = database.db_session.query(models.User).filter_by(login =login, password=password).first()

     if result:
          session['logged_in'] = True
          session['user_id'] = result.id
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
    database.init_db()
    session_user_id = session.get('user_id')

    if request.method == "POST":

         if user_id == session_user_id:
             return "You can edit your profile"

         first_name = request.form['first_name']
         last_name = request.form['last_name']
         login = request.form.get('login')
         email = request.form['email']
         password = request.form['password']
         birth_date = parser.parse(request.form['birth_date'])
         phone_number = request.form['phone']
         photo = request.form['photo']
         additional_info = request.form['additional_info']
         stmt = update(models.User).where(models.User.id == user_id).values(first_name=first_name, last_name=last_name, login=login, email=email, password=password, birth_date=birth_date, phone_number=phone_number, additional_info=additional_info)
         database.db_session.execute(stmt)
         database.db_session.commit()

         return 'User profile updated'
             #return render_template("user_profile.html", user_id=user_id)
    else:
        query_user_by_id = select(models.User).where(models.User.id == user_id)
        user_by_id = database.db_session.execute(query_user_by_id).scalar_one()

        if session_user_id is None:
            user_by_session = 'No user in session'
        else:
            query_user_by_session = select(models.User).where(models.User.id == session_user_id)
            user_by_session = database.db_session.execute(query_user_by_session).scalar_one()
        database.db_session.commit()

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
    films_query = select(models.Film)
    for key, value in filter_params.items():
        if value:
            if key == 'name':
                films_query = films_query.where(models.Film.name.like(f'%{value}%'))

            else:
                if key == 'rating':
                    value = float(value)
                    films_query = films_query.where(models.Film.rating == value)
                if key == 'country':
                    films_query = films_query.where(models.Film.country == value)
                if key == 'year':
                    films_query = films_query.where(models.Film.year == int(value))

    films = films_query.order_by(models.Film.added_at.desc())
    result_films = database.db_session.execute(films).scalars()
    countries = select(models.Country)
    result_countries = database.db_session.execute(countries).scalars()
    return render_template('films.html', films=result_films, countries=result_countries)

@app.route("/films", methods=["POST"])
@decorator_check_login
def film_add():
    database.init_db()

    data = request.get_json() or {}
    name = data.get('name')
    poster = data.get('poster')
    description = data.get('description')
    rating = data.get('rating')
    country = data.get('country')

    if not name:
        return jsonify({'error': 'Name is required'}),400

    new_film = models.Film(name=name, poster=poster, description=description, rating=rating, country=country)
    result = database.db_session.add(new_film)
    database.db_session.commit()

    return jsonify({'film_id': new_film.id}), 201

@app.route("/films/<film_id>", methods=["GET"])
def film_info(film_id):
    database.init_db()

    film_by_id = select(models.Film).where(models.Film.id == film_id)
    result_film_by_id = database.db_session.execute(film_by_id).scalar_one()

    actors = select(models.Actor).join(models.ActorFilm, models.Actor.id == models.ActorFilm.actor_id).where(models.ActorFilm.film_id == film_id)
    result_actors = database.db_session.execute(actors).scalars()

    genres = select(models.Genre).join(models.GenreFilm, models.Genre.genre == models.GenreFilm.genre_id).where(models.GenreFilm == film_id)
    result_genres = database.db_session.execute(genres).scalars()

    return jsonify({
        'id': result_film_by_id.id,
        'name': result_film_by_id.name,
        'poster': result_film_by_id.poster,
        'description': result_film_by_id.description,
        'rating': result_film_by_id.rating,
        'country': result_film_by_id.country,
        'added_at': result_film_by_id.added_at,
        'actors': [actor.name for actor in result_actors],
        'genres': [genre.genre for genre in result_genres]
    })

@app.route("/films/<film_id>", methods=["DELETE"])
def film_delete(film_id):
    return f"Film {film_id} deleted"

@app.route("/films/<int:film_id>", methods=["PUT"])
@decorator_check_login
def film_update(film_id):
    data = request.get_json() or {}
    database.init_db()

    new_film_query = select(models.Film).where(models.Film.id == film_id)#update(models.Film).where(models.Film.id == film_id).values(name=data.get('name'), poster=data.get('poster'), description=data.get('description'), rating=data.get('rating'), country=data.get('country'))
    new_film = database.db_session.execute(new_film_query).scalar_one()

    new_film.name = data.get('name')
    new_film.poster = data.get('poster')
    new_film.description = data.get('description')
    new_film.rating = data.get('rating')
    new_film.country = data.get('country')

    database.db_session.add(new_film)
    database.db_session.commit()



    return jsonify({'film_id': new_film.id})


@app.route("/films/<film_id>/rating", methods=["POST"])
def film_rating (film_id):
    return f"Film {film_id} rated"

@app.route("/films/<film_id>/rating", methods=["GET"])
def film_rating_info(film_id):
    database.init_db()
    ratings_query = select(models.Feedback).where(models.Feedback.film_id == film_id)
    ratings = database.db_session.execute(ratings_query).scalars()

    grades_query = select(func.avg(models.Feedback.grade).label('average'), func.count(models.Feedback.id).label('ratings_count')).where(models.Feedback.film_id == film_id)
    grade = database.db_session.execute(grades_query).fetchone()

    return jsonify({
        'film_id': film_id,
        'average_rating': grade,
        'ratings_count': grade,
        'ratings': ratings
    })


@app.route("/films/<film_id>/rating/<feedback_id>", methods=["PUT"])
def film_rating_update(film_id, feedback_id):
    return f"Film {film_id} rating updated {feedback_id}"

@app.route("/films/<film_id>/rating/<feedback_id>", methods=["DELETE"])
def film_rating_deletee(film_id, feedback_id):
    return f"Film {film_id} feedback {feedback_id} deleted"

@app.route("/films/<film_id>/rating/<feedback_id>/feedback", methods=["GET"])
def film_rating_feedback(film_id, feedback_id):
    database.init_db()
    stmt = (select(models.Feedback).where(models.Feedback.film_id == film_id, models.Feedback.id == feedback_id))
    feedback = database.db_session.execute(stmt).scalar_one_or_none()

    return jsonify({
        "id": feedback.id,
        "film_id": feedback.film_id,
        "user_id": feedback.user_id,
        "grade": feedback.grade,
        "description": feedback.description
    })

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


