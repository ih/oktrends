from sqlalchemy import create_engine
from Queue import PriorityQueue
from sqlalchemy.orm import mapper

class User(object):
    def __init__(self, userid, latitude, longitude):
        self.userid = userid
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return "<User('%s','%s','%s')>" % (self.userid, self.latitude, self.longitude)
engine = create_engine('mysql://root:password@localhost/first')
connection=engine.connect()
result=connection.execute("select * from usr_locations")
for row in result:
    print row
