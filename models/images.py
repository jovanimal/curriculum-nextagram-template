from models.base_model import BaseModel
import peewee as pw
from models.user import User
from playhouse.hybrid import hybrid_property


class Image(BaseModel):
    user = pw.ForeignKeyField(User, backref="users")
    user_image = pw.CharField(null=True)
    caption = pw.CharField(null=True)

    @hybrid_property
    def user_image_url(self):
        return f"http://nextagram-jovan.s3.ap-southeast-1.amazonaws.com/{self.user_image}"

    @hybrid_property
    def total_donations(self):
        from models.donation import Donation
        total = 0
        for donation in Donation.select().where(Donation.image_id == self.id):
            total = total + donation.amount
        return round(total)
