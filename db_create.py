from app import db
from models import Recipe


#run when adding new columns in testing, will delete previous data.
#db.drop_all()

db.create_all()

db.session.add(Recipe("chicken feet","/static/img/upload_img/chickenfeet.jpeg","one of my fav.","Ingredients: 7 chicken feet.<br>Steps:eat it raw!!!"))

db.session.add(Recipe("sweet and sour cabbage","/static/img/upload_img/spicysourlettuc.jpeg","refreshing", "Ingredients: ...<br>Steps:..."))




db.session.commit()
