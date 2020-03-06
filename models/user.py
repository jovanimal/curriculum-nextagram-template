from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
import re
from playhouse.hybrid import hybrid_property, hybrid_method


class User(BaseModel):
    email = pw.CharField(unique=True, null=False)
    password = pw.CharField(unique=False, null=False)
    username = pw.CharField(unique=True, null=False)
    profile_image = pw.CharField(null=True)

    def validate(self):
        mixed = any(letter.islower() for letter in self.password) and any(
            letter.isupper() for letter in self.password)

        if len(self.password) < 6 or len(self.password) > 12 and not self.id:
            self.errors.append('Password must be between 6-12 characters')
        elif not mixed and not self.id:
            self.errors.append(
                'Password must contain an upper and a lower case letter')
        elif not re.search("(?=.*[@$!%*#?&])", self.password) and not self.id:
            self.errors.append(
                "Password must contain at least one special character")
        else:
            if not self.id:
                self.password = generate_password_hash(self.password)

        existing_email = User.get_or_none(User.email == self.email)
        if existing_email and not existing_email.id == self.id:
            self.errors.append('Accounts with this email already in use')

        return True

    @hybrid_property
    def profile_image_url(self):
        return f"http://nextagram-jovan.s3.ap-southeast-1.amazonaws.com/{self.profile_image}"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    # def get_id(self):
    #     return self.id

    @hybrid_method
    def is_following(self, user):
        from models.following import Following
        return True if Following.get_or_none((Following.idol_id == user.id) and (Following.fan_id == self.id)) else False
