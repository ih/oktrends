from p4 import *
import unittest
from copy import copy

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
n=Rectangle(Coord(100,0),Coord(0,100))
urq=UniqueRectangleQueue()
t=Rectangle(Coord(100,1),Coord(0,100))
s=Rectangle(Coord(1,0),Coord(0,1))
urq.put(r)
allUsers=[User(n,n,n) for n in range(10)]

l=[r,t,n,copy(t)]

neighbors(s)


