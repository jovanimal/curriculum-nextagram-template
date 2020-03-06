from flask import Blueprint, render_template, request, url_for, redirect, flash
from models.user import User
from models.images import Image
from models.donation import Donation
from flask_login import current_user, login_required
import braintree

donations_blueprint = Blueprint('donations',
                                __name__,
                                template_folder='templates')

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="ytjkph8r4p93tgg3",
        public_key="wjdm59tqjbm26m9f",
        private_key="98736b75a95f6321a71b0d058dd0e730"
    )
)


@donations_blueprint.route('/<image_id>/new', methods=['GET'])
@login_required
def new(image_id):
    image = Image.get_or_none(Image.id == image_id)

    if not image:
        flash('No image found with id provided', 'warning')
        return redirect(url_for('users.index'))

    client_token = gateway.client_token.generate()

    if not client_token:
        flash('Unable to obtain token', 'warning')
        return redirect(url_for('users.index'))

    return render_template('donations/new.html', image=image, client_token=client_token)


@donations_blueprint.route('/<image_id>', methods=['POST'])
@login_required
def create(image_id):

    nonce = request.form.get('payment_method_nonce')
    if not nonce:
        flash(f"Error with payment method nonce", 'warning')
        return redirect(url_for('users.index'))

    image = Image.get_or_none(Image.id == image_id)

    # if not image:
    #     flash('Could not find image with provided ID', 'warning')
    #     return redirect(url_for('users.index'))

    amount = request.form.get('amount')

    if not amount:
        flash('No amount is provided for donation', 'warning')
        return redirect(url_for('users.index'))

    result = gateway.transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce,
        "options": {
            "submit_for_settlement": True
        }
    })

    if not result.is_success:
        flash('unable to complete transaction', 'warning')
        return redirect(request.referrer)

    donation = Donation(amount=amount, image=image.id,
                        user=current_user.id)

    if not donation.save():
        ('Donation successfull but error creating record', 'warning')
        return redirect(url_for('users.index'))

    flash('You have successfully donated. Thank you!')
    return redirect(url_for('sessions.show', username=current_user.username))
