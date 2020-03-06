from flask import Blueprint, render_template, request, url_for, redirect, flash
from models.user import User
from models.images import Image
from models.following import Following
from flask_login import current_user

follows_blueprint = Blueprint("follows",
                              __name__,
                              template_folder='templates')


@follows_blueprint.route('/<idol_id>', methods=['POST'])
def create(idol_id):
    idol = User.get_or_none(User.id == idol_id)

    if not idol:
        flash('No user found with this id')
        return redirect(url_for('sessions.index'))
        # modify this to show homepage HOME in sessions

    new_follow = Following(fan_id=current_user.id, idol_id=idol.id)

    if not new_follow.save():
        flash('Error in following this user', 'warning')
        return redirect(url_for('users.show', username=idol.username))

    else:
        flash(f'You are now following {idol.username}')
        return redirect(url_for('users.show', username=idol.username))

    flash('Following request has sent ! Please wait for approval.')


@follows_blueprint.route('/<idol_id>/delete', methods=['POST'])
def delete(idol_id):
    follow = Following.get_or_none(Following.idol_id == idol.id) and (
        Following.fan_id == current_user.id)

    if follow.delete_instance():
        flash(f'You have unfollowed {follow.idol.username}')
        return redirect(url_for('users.show', username=follow.idol.username))
