from p4 import *
import unittest
from copy import copy

#4x4 gridTest
us=[]
us.append(User(0,.5,2.5))
us.append(User(1,.5,1.5))
us.append(User(2,1.5,1.5))
us.append(User(3,2.5,.5))
us.append(User(4,3.5,3.5))
start=Rectangle(Coord(4,0),Coord(0,4))
[start.addUser(u) for u in us]
rq=RectangleQueue()
rq.put(start)
s=findSeeds(rq)
s0=s[0]
test(start.users)
print(neighbors(s0))

#intersection test
r1=Rectangle(Coord(2,0),Coord(0,2))
r2=Rectangle(Coord(4,1),Coord(1,4))
r3=Rectangle(Coord(3,2),Coord(2,3))
r4=Rectangle(Coord(2,1),Coord(1,4))
#extensionTest

ct=Rectangle(Coord(1,1),Coord(0,2))
[ct.addUser(u) for u in us]
nt=Rectangle(Coord(2,1),Coord(1,2))
nt.extendRectangle(ct)
st=Rectangle(Coord(0,1),Coord(-1,2))
[st.addUser(u) for u in us]
st.extendRectangle(ct)

et=Rectangle(Coord(1,2),Coord(0,3))
print "test:"+str(et)

#ct.extendRectangle(et)
et.extendRectangle(ct)

#growRectangles(s)
#print s
# p1=Coord(90,0)
# p2=Coord(0,90)
# r=Rectangle(p1,p2)
# r.addUser(User(1,5,5))
# r.addUser(User(2,5,60))
# r.addUser(User(3,60,65))
# r.addUser(User(4,63,62))
# r.addUser(User(5,20,5))
# r.addUser(User(6,23,10))
# r.addUser(User(7,76,16))
# rq=RectangleQueue()
# rq.put(r)
# n=Rectangle(Coord(100,0),Coord(0,100))
# urq=UniqueRectangleQueue()
# t=Rectangle(Coord(100,1),Coord(0,100))
# s=Rectangle(Coord(1,0),Coord(0,1))
# urq.put(r)
# allUsers=[User(n,n,n) for n in range(10)]
# e=Rectangle(Coord(1,1),Coord(0,2))
# print s
# s.extendRectangle(e)
# print s
# l=[r,t,n,copy(t)]



# ss=findSeeds(rq)
# print ss
# print [neighbors(sq) for sq in ss]
# #rs=growRectangles(ss)
