import sys
from sqlalchemy import create_engine
from Queue import PriorityQueue
from copy import copy
import pdb

rectangleNum = 5
rectangles = []
areaLimit = 100 #square miles
meshSize = 1 #square miles
seedLimit = areaLimit/meshSize #the most number of seeds one might need
allUsers = []
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
        allUsers.append(u) #change this to insert user into two lists sorted by lat and lon; eventually used in populate
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
        seed=seeds.pop(0)
        growthQueue=UniqueRectangleQueue()
        growthQueue.put(seed)
        # hypRec is our hypothesis rectangle that gets extended to cover the most populated neighboring squares
        hypRec = copy(seed) 
        while area(hypRec)<areaLimit and growthQueue:
            mostPopulated = growthQueue.get()
            for neighbor in neighbors(mostPopulated):
                try: 
                    seeds.remove(neighbor) #populating neighbors can be optimized by using the already populated seeds if the seed is a neighbor
                except ValueError:
                    None
                growthQueue.put(neighbor)
            hypRec.extendRectangle(mostPopulated)
        rectangles.append(hypRec)

def populate(rectangle,population):
    #highly inefficient (can be improved by using two lists of users sorted by lat and lon respectively
    for user in population:
        assign(user, [rectangle])

def neighbors(rectangle):
    """return neighboring rectangles with the users who exist in them"""
    assert area(rectangle) == meshSize
    ns = [north(rectangle),west(rectangle),east(rectangle),south(rectangle)]
    [populate(n,allUsers) for n in ns]
    return ns

def north(rectangle):
    if rectangle.nw.lat+rectangle.height <= 90:
        nw=Coord(rectangle.nw.lat+rectangle.height, rectangle.nw.lon)
        se=Coord(rectangle.nw.lat, rectangle.se.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.nw.lat == 90
        assert False
def west(rectangle):
    if rectangle.nw.lon-rectangle.width >= -180:
        nw=Coord(rectangle.nw.lat, rectangle.nw.lon-rectangle.width)
        se=Coord(rectangle.se.lat, rectangle.nw.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.nw.lon == -180
        assert False
def east(rectangle):
    if rectangle.se.lon+rectangle.width <= 180:
        nw=Coord(rectangle.nw.lat, rectangle.se.lon)
        se=Coord(rectangle.se.lat, rectangle.se.lon+rectangle.width)
        return Rectangle(nw,se)
    else:
        assert rectangle.se.lon == 180
        assert False
def south(rectangle):
    if rectangle.se.lat-rectangle.height >= -90:
        nw=Coord(rectangle.se.lat, rectangle.nw.lon)
        se=Coord(rectangle.se.lat-rectangle.height, rectangle.se.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.se.lat == -90
        assert False

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

            
class RectangleQueue(PriorityQueue):
    def put(self,rectangle):
        #we use the negative b/c priority queues are implemented as min heaps in python
        PriorityQueue.put(self,(-rectangle.popSize(), rectangle))
    def get(self):
        (popNum,rectangle) = PriorityQueue.get(self)
        return rectangle

class UniqueRectangleQueue(RectangleQueue):
    """A priority queue that can only have a rectangle inserted once"""
    def __init__(self):
        RectangleQueue.__init__(self)
        self.History = set()
    def put(self,rectangle):
        if rectangle not in self.History:
            self.History.add(rectangle)
            RectangleQueue.put(self, rectangle)


class Rectangle:
    def __init__(self, northWest, southEast):
        self.nw = northWest
        self.se = southEast
        self.height = northWest.lat-southEast.lat
        assert(self.height > 0)
        self.width = southEast.lon-northWest.lon
        assert(self.width > 0)
        self.users = []

    def __repr__(self):
        return str(self.nw)+","+str(self.se)+" Contains:" + str(len(self.users))
    def __eq__(self, other):
        return self.nw == other.nw and self.se == other.se
    def __hash__(self):
        return hash((self.nw,self.se))
    def addUser(self,user):
        self.users.append(user)
    def popSize(self):
        return len(self.users)
    def extenRectangle(self, expansion):
        case 

def area(rectangle):
    return rectangle.height*rectangle.width

class Coord:
    def __init__(self, lat, lon):
        self.lat=lat
        self.lon=lon
    def __repr__(self):
        return "("+str(self.lat)+","+str(self.lon)+")"
    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon
    def __hash__(self):
        return hash((self.lat,self.lon))

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


