from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import session

try:
    from database import register_user, login_user
except ImportError:
    from .database import register_user, login_user

auth = Blueprint("auth", __name__)

# ---------------- Login ----------------

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")

        user = login_user(email, password)

        if user:

            session["user"] = user["email"]

            session["name"] = user["full_name"]

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid Email or Password"
        )

    return render_template("login.html")

# ---------------- Register ----------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")

        confirm = request.form.get("confirm", "")

        if password != confirm:

            return render_template(
                "register.html",
                error="Passwords do not match"
            )

        status = register_user(
            name,
            email,
            password
        )

        if status:

            return render_template(
                "login.html",
                success="Account Created Successfully! Please log in."
            )

        return render_template(
            "register.html",
            error="Email Already Exists"
        )

    return render_template("register.html")

