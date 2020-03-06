from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from models.user import User
from models.images import Image
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from instagram_web.util.s3_uploader import upload_file_to_s3
from instagram_web.helpers.google_oauth import oauth

sessions_blueprint = Blueprint('sessions',
                               __name__,
                               template_folder='templates')


@sessions_blueprint.route('/home', methods=['GET'])
def index():
    get_images = Image.select().where(Image.user_id == current_user.id)
    return render_template('sessions/home.html', get_images=get_images)


@sessions_blueprint.route('/login', methods=['POST'])
def login():
    # username = request.form.get("user_name")
    password = request.form.get("password")
    # user = User.get_or_none(User.username == username)

    username_get = User.get_or_none(
        User.username == request.form.get('user_name'))

    if username_get and check_password_hash(username_get.password, password):
        login_user(username_get)
        flash('You have logged in', 'success')
        # session['user'] = username_get.username
        return redirect(url_for('sessions.new'))

    else:
        flash("Username/Password is incorrect, please try again", "danger")
        return redirect(url_for('sessions.index'))


@sessions_blueprint.route('/<username>', methods=["GET"])
def show(username):
    if current_user:
        get_images = Image.select().where(Image.user_id == current_user.id)
        return render_template('sessions/show.html', currentuser_username=current_user.username, get_images=get_images)


@sessions_blueprint.route('/new')
def new():

    # if current_user:
    #     return render_template("sessions/profile.html")
    # else:
    return render_template("sessions/new.html")


@sessions_blueprint.route('/logout')
def logout():
    # session.pop('user', None)
    logout_user()
    flash("Successfully logged out", 'success')
    return redirect(url_for('sessions.new'))
    # password_to_check = request.form['password']
    # # password hash stored in database for a specific user
    # hashed_password = user.hashed_password

    # # what is result? Test it in Flask shell and implement it in your view function!
    # result = check_password_hash(hashed_password, password_to_check)


@sessions_blueprint.route('/upload/images', methods=['POST'])
@login_required
def upload_images():
    if "user_image" not in request.files:
        flash('No image has been provided', 'warning')
        return redirect(url_for('session.new'))

    file = request.files.get("user_image")
    caption = request.form.get("caption")

    file.filename = secure_filename(file.filename)

    if not upload_file_to_s3(file):
        flash('Oops, something went wrong while uploading', 'warning')
        return redirect(url_for('sessions.new'))

    user = User.get_or_none(User.id == current_user.id)

    img_upload = Image(user=user.id, user_image=file.filename, caption=caption)

    img_upload.save()

    flash('Successfully uploaded Image', 'success')
    return redirect(url_for('sessions.new'))


@sessions_blueprint.route("/google_login")
def google_login():
    redirect_uri = url_for('sessions.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@sessions_blueprint.route("/authorize/google")
def authorize():
    oauth.google.authorize_access_token()
    email = oauth.google.get(
        'https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    if user:
        login_user(user)
        flash('You have successfully logged in')
        return redirect(url_for('sessions.show', username=current_user.username))
    else:
        return redirect(url_for('users.new'))
