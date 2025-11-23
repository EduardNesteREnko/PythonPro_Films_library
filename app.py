from flask import Flask

app = Flask(__name__)

@app.route("/")
def main_page():
    return "Hello world!"

@app.route("/register", methods=["POST"])
def user_register():
    return "Register"

@app.post("/login")
def user_login():
    return "Login"

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
    return f"Films"

@app.route("/films", methods=["POST"])
def film_add():
    return f"Film added"

@app.route("/films/<film_id>", methods=["GET"])
def film_info(film_id):
    return f"Film {film_id}"

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
    return f"Film rating {film_id}"


@app.route("/films/<film_id>/rating/<feedback_id>", methods=["PUT"])
def film_rating_update(film_id, feedback_id):
    return f"Film {film_id} rating updated {feedback_id}"

@app.route("/films/<film_id>/rating/<feedback_id>", methods=["DELETE"])
def film_rating_deletee(film_id, feedback_id):
    return f"Film {film_id} feedbacl {feedback_id} deleted"

@app.route("/films/<film_id>/rating/<feedback_id>/feedback", methods=["GET"])
def film_rating_feedback(film_id, feedback_id):
    return f"Film {film_id} rating {feedback_id} feedback"

@app.route("/user/<user_id>/list", methods=["GET", "POST"])
def user_lists(user_id):
    return f"Lists of {user_id}"

@app.route("/user/<user_id>/list", methods=["DELETE"])
def user_lists_delete(user_id):
    return f"List {user_id} deleted"

@app.route("/user/<user_id>/list/<list_id>", methods=["GET", "POST"])
def user_lists_delete(user_id, list_id):
    return f"User {user_id} list item {list_id}"

@app.route("/user/<user_id>/list/<list_id>/<film_id>", methods=["DELETE"])
def user_list_item_delete( user_id, list_id):
    return f"User {user_id} list item {list_id} deleted"


if __name__ == '__main__':
    app.run(debug=True)


