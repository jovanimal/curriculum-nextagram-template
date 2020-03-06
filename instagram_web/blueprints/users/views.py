from flask import Blueprint, render_template, request, url_for, redirect, flash
from models.user import User
from werkzeug.security import generate_password_hash
from werkzeug import secure_filename
from flask_login import current_user, login_required
from instagram_web.util.s3_uploader import upload_file_to_s3

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/new/', methods=['POST'])
def user_create():
    user_name = request.form.get('user_name')
    email = request.form.get('email')
    password = request.form.get('password')

    user = User(username=user_name, email=email, password=password)

    if user.save():
        flash('Successfully signed up!', 'success')
        return redirect(url_for('sessions.index'))
    else:
        for error in user.errors:
            flash(error, 'danger')
        return redirect(url_for('users.new'))


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    user = current_user
    return render_template('users/show.html', user=user)


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/info', methods=['GET'])
@login_required
def edit(id):
    user = User.get_or_none(User.id == id)
    return render_template('users/edit.html', user=user)


@users_blueprint.route('/<id>/edit', methods=['POST'])
@login_required
def update(id):
    user = User.get_by_id(id)
    # id = current_user.id
    new_username = request.form.get("user_name")
    user.username = new_username

    new_email = request.form.get("email")
    user.email = new_email
    # if current_user == user:
    if user.save():
        flash("Your username/email has changed successfully", "success")
        return redirect(url_for("sessions.new"))
    else:
        flash("Something's wrong, please try again", "danger")
        return redirect(url_for("sessions.new"))


@users_blueprint.route('/upload', methods=['POST'])
@login_required
def upload():

    if "profile_image" not in request.files:
        flash('No image has been provided', 'warning')
        return redirect(url_for('users.edit', id=current_user.id))

    file = request.files.get("profile_image")

    file.filename = secure_filename(file.filename)

    if not upload_file_to_s3(file):
        flash('Oops, something went wrong while uploading', 'warning')
        return redirect(url_for('users.edit', id=current_user.id))

    user = User.get_or_none(User.id == current_user.id)

    user.profile_image = file.filename

    user.save()

    flash('Successfully uploaded profile Image', 'success')
    return redirect(url_for('users.edit', id=user.id))
