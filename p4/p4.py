import sys
from sqlalchemy import create_engine
from Queue import PriorityQueue
from copy import copy,deepcopy
import pdb

northLimit=4
southLimit=-4
eastLimit=8
westLimit=-8
rectangleNum = 5

areaLimit = 2 #square miles
meshSize = 1 #square miles
seedLimit = rectangleNum*areaLimit/meshSize #the most number of seeds one might need
allUsers = []

def test(users):
    global allUsers
    allUsers=users

def preprocess(dbuser,dbpass,host):
    s='mysql://'+dbuser+':'+dbpass+'@'+host+'/'+'okcupid'
#    s='mysql://'+dbuser+':'+dbpass+'@localhost/first'
#    engine = create_engine('mysql://'+dbuser+':'+dbpass+'+@localhost/first')
    engine = create_engine(s)
    connection=engine.connect()
    data=connection.execute("select * from usr_locations")
    west=Rectangle(Coord(northLimit,westLimit),Coord(southLimit,0))
    east=Rectangle(Coord(northLimit,0),Coord(southLimit,eastLimit))
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
    rectangles = []
    while len(rectangles) < rectangleNum and seeds:
        seed=seeds.pop(0)
#        pdb.set_trace()
        if not intersects(seed,rectangles):
            # hypRec is the hypothesis rectangle that gets extended to cover the most populated neighboring squares
            hypRec = copy(seed) 
            growthQueue=UniqueRectangleQueue()#change this to clear the queue instead of creating a new one?
            [growthQueue.put(neighbor) for neighbor in neighbors(seed) if not intersects(neighbor, rectangles)]
            grown=False #flag changes to true once extension attempt surpasses arealimit
            while not grown and growthQueue:
                mostPopulated = growthQueue.get()
                #make sure hypRec didn't cover up neighbors placed in growthQueue
                if not intersects(mostPopulated, [hypRec]): 
                #check if extending the hypothesis rectangle would intersect anything in rectangles
                    testExpand=Rectangle(deepcopy(hypRec.nw),deepcopy(hypRec.se))
                    testExpand.extendRectangle(mostPopulated)
                    if area(testExpand) > areaLimit:
                        grown = True
                    if not intersects(testExpand, rectangles) and not grown:
                        hypRec.extendRectangle(mostPopulated)
          
                        #only add neighbors of mostPopulated if the hypothesis was extended
                        [growthQueue.put(neighbor) for neighbor in neighbors(mostPopulated) if not intersects(neighbor, rectangles)]
            rectangles.append(hypRec)
            #insert remaining populated elements in growthQueue into seeds (maybe make seeds a pqueue since we don't remove anything)
    return rectangles

def intersects(rectangle, rectangles):
    return any([rectangle.intersects(r) for r in rectangles])

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
    if rectangle.nw.lat+rectangle.height() <= northLimit:
        nw=Coord(rectangle.nw.lat+rectangle.height(), rectangle.nw.lon)
        se=Coord(rectangle.nw.lat, rectangle.se.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.nw.lat == northLimit
        return rectangle
def west(rectangle):
    if rectangle.nw.lon-rectangle.width() >= westLimit:
        nw=Coord(rectangle.nw.lat, rectangle.nw.lon-rectangle.width())
        se=Coord(rectangle.se.lat, rectangle.nw.lon)
        return Rectangle(nw,se)
    else:
        assert rectangle.nw.lon == westLimit
        return rectangle
def east(rectangle):
    if rectangle.se.lon+rectangle.width() <= eastLimit:
        nw=Coord(rectangle.nw.lat, rectangle.se.lon)
        se=Coord(rectangle.se.lat, rectangle.se.lon+rectangle.width())
        return Rectangle(nw,se)
    else:
#        assert rectangle.se.lon == eastLimit
        return rectangle 
def south(rectangle):
    if rectangle.se.lat-rectangle.height() >= southLimit:
        nw=Coord(rectangle.se.lat, rectangle.nw.lon)
        se=Coord(rectangle.se.lat-rectangle.height(), rectangle.se.lon)
        return Rectangle(nw,se)
    else:
#        assert rectangle.se.lat == southLimit
        return rectangle

def findSeeds(rectangleQueue):
    """return most populated squares of size dependent on mesh_size"""
    seeds = []
    while len(seeds) < seedLimit and not rectangleQueue.empty():
#        pdb.set_trace()
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
        self.users = set()
    def height(self):
        assert (self.nw.lat-self.se.lat)>0
        return self.nw.lat-self.se.lat
    def width(self):
        assert(self.se.lon-self.nw.lon)>0
        return self.se.lon-self.nw.lon
    def intersects(self, other):
#        pdb.set_trace()
        selfInOther = other.contains(self.nw) or other.contains(self.se) or other.contains(Coord(self.se.lat,self.nw.lon)) or other.contains(Coord(self.nw.lat,self.se.lon))
        otherInSelf = self.contains(other.nw) or self.contains(other.se) or self.contains(Coord(other.se.lat,other.nw.lon)) or self.contains(Coord(other.nw.lat,other.se.lon))
        selfCenterInOther = other.contains(Coord(self.nw.lat-self.height()/2.0,self.se.lon-self.width()/2.0))
        otherCenterInSelf = self.contains(Coord(other.nw.lat-other.height()/2.0,other.se.lon-other.width()/2.0))
        return selfInOther or otherInSelf or selfCenterInOther or otherCenterInSelf
    def contains(self, coordinate):
        return coordinate.lat<self.nw.lat and coordinate.lat>self.se.lat and coordinate.lon <self.se.lon and coordinate.lon > self.nw.lon
    def __repr__(self):
        return str(self.nw)+","+str(self.se)+" Contains:" + str(len(self.users))
    def __eq__(self, other):
        return self.nw == other.nw and self.se == other.se
    def __hash__(self):
        return hash((self.nw,self.se))
    def addUser(self,user):
        self.users.add(user)
    def popSize(self):
        return len(self.users)
    def extendRectangle(self, expansion):
        [self.addUser(u) for u in expansion.users]
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
    return rectangle.height()*rectangle.width()

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
    def __eq__(self, other):
        return self.userid == other.userid
    def __hash__(self):
        return hash(self.userid)

# get all data from the database
# dbuser, dbpass, host = sys.argv[1],sys.argv[2]
# ans = growRectangles(findSeeds(preprocess(dbuser,dbpass,host)))
# for r in ans:
#     print r
#     for user in r.users:
#         print user



# p1=Coord(100,0)
# p2=Coord(0,100)
# r=Rectangle(p1,p2)
# r.addUser(User(1,5,5))
# r.addUser(User(2,5,60))
# r.addUser(User(3,60,65))
# r.addUser(User(4,63,62))
# r.addUser(User(5,99,5))
# r.addUser(User(6,89,10))
# r.addUser(User(7,76,16))
# rq=RectangleQueue()
# rq.put(r)



# p1=Coord(20,0)
# p2=Coord(0,20)
# r=Rectangle(p1,p2)
# rs=divide(r)
# u=User(2333,10,10)
# assign(u,rs)
# rq=RectangleQueue()
# for rec in rs:
#     rq.put(rec)


