from datetime import datetime
from project.models import Notification
from project import db

def create_notifition(user_id,notification):
    notifition_comp = Notification(user_id=user_id,notification=notification,create_at=datetime.now())
    db.session.add(notifition_comp)
