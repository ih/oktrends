import sys
from sqlalchemy import create_engine
from Queue import PriorityQueue
import pdb

rectangleNum = 5
rectangles = []
areaLimit = 100 #square miles
meshSize = 1 #square miles
seedLimit = areaLimit/meshSize #the most number of seeds one might need
def preprocess(dbuser,dbpass):
    s='mysql://'+dbuser+':'+dbpass+'@localhost/first'
#    engine = create_engine('mysql://'+dbuser+':'+dbpass+'+@localhost/first')
    engine = create_engine(s)
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

def findRectangles(dbuser,dbpass):
    #find squares with area meshSize that are most populated
    seeds = findSeeds(preprocess(dbuser,dbpass)) #a collection with a delete function
    while len(rectangles) < rectangleNum and seeds:
        # mostPopulated=popMostPopulated(seeds) 
        seed=popMostPopulated(seeds)
        growthQueue=UniqueRectangleQueue()
        growQueue.put(seed)
        # hypRec is our hypothesis rectangle that grows to cover the most populated seeds
        hypRec = copy(seed) 
        while area(hypRec)<areaLimit and growthQueue:
            mostPopulated = growthQueue.get()
            for neighbor in neighbors(mostPopulated):
                try: 
                    seeds.remove(neighbor)
                except ValueError:
                    None
                growthQueue.put(neighbor)
            hypRec.extendRectangle(mostPopulated)
        rectangles.append(hypRec)

def findSeeds(rectangleQueue):
    """return most populated squares of size dependent on mesh_size"""
    seeds = []
    while len(seeds) < seedLimit and not rectangleQueue.empty():
        mostPopulated = rectangleQueue.get()
        if area(mostPopulated) <= meshSize:
            seeds.append(mostPopulated)
        else:
            newRectangles = divide(mostPopulated)
            for user in mostPopulated.users:
                assign(user, newRectangles)

            for rectangle in newRectangles:
                if rectangle.popSize()>0:
                    rectangleQueue.put(rectangle)
#        pdb.set_trace()
    return seeds

def divide(rectangle):
    """returns a set of subrectangles of rectangle"""
    y = rectangle.nw.lat
    x = rectangle.nw.lon
    b = rectangle.se.lat
    a = rectangle.se.lon
    midh = ((y-b)/2.0)+b
    midw = ((a-x)/2.0)+x
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

class UniqueRectangleQueue():
    """A priority queue for rectangles that can only have a rectangle """

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

#get all data from the database
# dbuser, dbpass = sys.argv[1],sys.argv[2]
# ans = findRectangles(preprocess(dbuser,dbpass))
# for r in ans:
#     print r
#     for user in r.users:
#         print user



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


