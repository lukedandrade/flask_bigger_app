from app import db, models
import datetime

#script para novos posts

user = models.User.query.get(1)
post = models.Post(body='my first post', timestamp=datetime.datetime.utcnow(), author=user)

db.session.add(post)
db.session.commit()