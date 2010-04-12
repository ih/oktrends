from sqlalchemy import create_engine
from Queue import PriorityQueue
import pdb

#get all data from the database

def preprocess():
    engine = create_engine('mysql://root:password@localhost/first')
    connection=engine.connect()
    data=connection.execute("select * from usr_locations")
    west=Rectangle(Coord(90,-180),Coord(-90,0))
    east=Rectangle(Coord(90,0),Coord(-90,180))
    for row in data:
        u=User(row[0],row[1],row[2])
        if u.pos.lon<=0:
            west.addUser(u)
        else:
            east.addUser(u)
    rq=RectangleQueue()
    rq.put(east)
    rq.put(west)
    return rq

rectangleNum = 3
rectangles = []
areaLimit = 300

def findRectangles(rectangleQueue):
    """finds a set of rectangles that hopefully contain the most number of people"""
    while len(rectangles) < rectangleNum and not rectangleQueue.empty():
        mostPopulated = rectangleQueue.get()
        if area(mostPopulated) <= areaLimit:
            rectangles.append(mostPopulated)
        else:
            newRectangles = divide(mostPopulated)
            for user in mostPopulated.users:
                assign(user, newRectangles)

            for rectangle in newRectangles:
                if rectangle.popSize()>0:
                    rectangleQueue.put(rectangle)
#        pdb.set_trace()
    return rectangles

def divide(rectangle):
    """returns a set of subrectangles of rectangle"""
    y = rectangle.nw.lat
    x = rectangle.nw.lon
    b = rectangle.se.lat
    a = rectangle.se.lon
    midh = ((y-b)/2)+b
    midw = ((a-x)/2)+x
    r1=Rectangle(rectangle.nw, Coord(lat=midh,lon=midw))
    r2=Rectangle(Coord(y,midw), Coord(midh,a))
    r3=Rectangle(Coord(midh,midw), rectangle.se)
    r4=Rectangle(Coord(midh,x), Coord(b,midw))
    return [r1,r2,r3,r4]

def assign(user, disjointRectangles):
    for rectangle in disjointRectangles:
        if isIn(user,rectangle):
            rectangle.addUser(user)
            break

def isIn(user,rectangle):
    return user.pos.lat<=rectangle.nw.lat and user.pos.lat>rectangle.se.lat and user.pos.lon <= rectangle.se.lon and user.pos.lon > rectangle.nw.lon

class RectangleQueue(PriorityQueue):
    def put(self,rectangle):
        #we use the negative b/c priority queues are implemented as min heaps in python
        PriorityQueue.put(self,(-rectangle.popSize(), rectangle))
    def get(self):
        (popNum,rectangle) = PriorityQueue.get(self)
        return rectangle

class Rectangle:
    def __init__(self, northWest, southEast):
        self.nw = northWest
        self.se = southEast
        self.users = []
    def __repr__(self):
        return str(self.nw)+","+str(self.se)+" Contains:" + str(len(self.users))
    def addUser(self,user):
        self.users.append(user)
    def popSize(self):
        return len(self.users)

def area(rectangle):
    length=rectangle.se.lon-rectangle.nw.lon
    height=rectangle.nw.lat-rectangle.se.lat
    return length*height

class Coord:
    def __init__(self, lat, lon):
        self.lat=lat
        self.lon=lon
    def __repr__(self):
        return "("+str(self.lat)+","+str(self.lon)+")"

class User:
    def __init__(self, userid, latitude, longitude):
        self.userid = userid
        self.pos = Coord(lat=latitude,lon=longitude)
    def __repr__(self):
        return str(self.userid)+":"+str(self.pos)

p1=Coord(100,0)
p2=Coord(0,100)
r=Rectangle(p1,p2)
r.addUser(User(1,5,5))
r.addUser(User(2,5,60))
r.addUser(User(3,60,65))
r.addUser(User(4,63,62))
r.addUser(User(5,99,5))
r.addUser(User(6,89,10))
r.addUser(User(7,76,16))
rq=RectangleQueue()
rq.put(r)



# p1=Coord(20,0)
# p2=Coord(0,20)
# r=Rectangle(p1,p2)
# rs=divide(r)
# u=User(2333,10,10)
# assign(u,rs)
# rq=RectangleQueue()
# for rec in rs:
#     rq.put(rec)


