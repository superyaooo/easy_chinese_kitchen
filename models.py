from app import db
import datetime
from datetime import date

class Recipe(db.Model):

    __tablename__ = "recipes"
    __table_args__ = {'extend_existing':True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.Date)
    img_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)


    def __init__(self, title, img_url, description, content, pub_date=None):
        self.title = title
        if pub_date is None:
            pub_date = datetime.date.today()
        self.pub_date = pub_date
        self.img_url = img_url
        self.content = content
        self.description = description



    def __repr__(self):
        return '<{}>'.format(self.title)
