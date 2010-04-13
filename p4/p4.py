import sys
from sqlalchemy import create_engine
from Queue import PriorityQueue
from copy import copy
import pdb

northLimit=4
southLimit=0
eastLimit=5
westLimit=0
rectangleNum = 2

areaLimit = 2 #square miles
meshSize = 1 #square miles
seedLimit = areaLimit/meshSize #the most number of seeds one might need
allUsers = []

def test(users):
    global allUsers
    allUsers=users

def preprocess(dbuser,dbpass):
    s='mysql://'+dbuser+':'+dbpass+'@localhost/first'
#    engine = create_engine('mysql://'+dbuser+':'+dbpass+'+@localhost/first')
    engine = create_engine(s)
    connection=engine.connect()
    data=connection.execute("select * from usr_locations")
    west=Rectangle(Coord(northLimit,westLimit),Coord(southLimit,0))
    east=Rectangle(Coord(northLimit,0),Coord(southLimit,northLimit))
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

def growRectangles(seeds):
    #find squares with area meshSize that are most populated
#    seeds = findSeeds(preprocess(dbuser,dbpass)) #a collection with a delete function
    rectangles = []
    pdb.set_trace()
    while len(rectangles) < rectangleNum and seeds:
        # mostPopulated=popMostPopulated(seeds)

        seed=seeds.pop(0)
        if not intersects(seed,rectangles):
            growthQueue=UniqueRectangleQueue()#change this to clear the queue instead of creating a new one?
            growthQueue.put(seed)
            # hypRec is our ectangle that gets extended to cover the most populated neighboring squares
            hypRec = copy(seed) 
            while area(hypRec)<areaLimit and growthQueue:
                mostPopulated = growthQueue.get()
                #make sure hypRec didn't cover up neighbors placed in growthQueue
                if not intersects(mostPopulated, [hypRec]): 
                #check if extending the hypothesis rectangle would intersect anything in rectangles
                    testExpand=Rectangle(hypRec.nw,hypRec.se)
                    testExpand.extendRectangle(mostPopulated)
                    if not intersects(testExpand, rectangles):
                        hypRec.extendRectangle(mostPopulated)
                        #only add neighbors of mostPopulated if the hypothesis was extended
                        [growthQueue.put(neighbor) for neighbor in neighbors(mostPopulated) if not intersects(neighbor, rectangles)]
        rectangles.append(hypRec)
    return rectangles

def populate(rectangle,population):
    #highly inefficient (can be improved by using two lists of users sorted by lat and lon respectively
    for user in population:
        assign(user, [rectangle])

def neighbors(rectangle):
#    pdb.set_trace()
    """return neighboring rectangles with the users who exist in them"""
    assert area(rectangle) <= meshSize
    ns = [north(rectangle),west(rectangle),east(rectangle),south(rectangle)]
    [populate(n,allUsers) for n in ns]
    return ns

def north(rectangle):
    if rectangle.nw.lat+rectangle.height <= northLimit:
        nw=Coord(rectangle.nw.lat+rectangle.height, rectangle.nw.lon)
        se=Coord(rectangle.nw.lat, rectangle.se.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.nw.lat == northLimit
        return rectangle
def west(rectangle):
    if rectangle.nw.lon-rectangle.width >= westLimit:
        nw=Coord(rectangle.nw.lat, rectangle.nw.lon-rectangle.width)
        se=Coord(rectangle.se.lat, rectangle.nw.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.nw.lon == westLimit
        return rectangle
def east(rectangle):
    if rectangle.se.lon+rectangle.width <= eastLimit:
        nw=Coord(rectangle.nw.lat, rectangle.se.lon)
        se=Coord(rectangle.se.lat, rectangle.se.lon+rectangle.width)
        return Rectangle(nw,se)
    else:
        assert rectangle.se.lon == eastLimit
        return rectangle 
def south(rectangle):
    if rectangle.se.lat-rectangle.height >= southLimit:
        nw=Coord(rectangle.se.lat, rectangle.nw.lon)
        se=Coord(rectangle.se.lat-rectangle.height, rectangle.se.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.se.lat == southLimit
        return rectangle

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
    def extendRectangle(self, expansion):
        #assumes expansion is a rectangle that borders the current rectanlge
        #this can eventually be rewritten to draw diagonal rectangles
        if expansion.nw.lat > self.nw.lat:
            self.nw.lat = expansion.nw.lat
        elif expansion.nw.lon < self.nw.lon:
            self.nw.lon = expansion.nw.lon
        elif expansion.se.lon > self.se.lon:
            self.se.lon = expansion.se.lon
        elif expansion.se.lat < self.se.lat:
            self.se.lat = expansion.se.lat
        else:
            None
            #extend over northern border
#            pdb.set_trace()
#            assert (self == expansion), (str(self)+' '+str(expansion))

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


