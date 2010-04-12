data = read.table("sample_user.csv", header=TRUE, sep=",")
#convert when to date objects
EST=as.Date(data$when,format("%a %b %d %H:%M:%S EST %Y"))
EDT=as.Date(data$when,format("%a %b %d %H:%M:%S EDT %Y"))
EST[is.na(EST)]=EDT[is.na(EST)]
dates=EST
data$date = dates

uid = "6617175564718198A"
bobid = "11326666288218198A"
caroleid = "33651685167798A"
danid = "1114331986687698A"
edenid = "1962289198A79798A"
frankid = "28577267294898A"
str(data)

tsend=sort(table(data$senderid),decreasing=TRUE)
trec = sort(table(data$receiverid),decreasing=TRUE)
#number of people where who got replies
length(intersect(names(tsend),names(trec)))
#data frame with number of messages sent and received indexed by user
dsend=data.frame(tsend)
drec=data.frame(trec)          
          interact=merge(dsend,drec, by="Var1")          
interact=interact[order(interact$Freq.x,decreasing=TRUE),]
interact$Var1=intersect(names(tsend),names(trec))
#barchart of interactions
barplot(t(data.matrix(interact))[2:3,2:17],beside=TRUE,xlab="users",ylab="# of messages", names.arg=substring(interact$Var1[2:17],1,4),las=2,col=c("red","blue"))

legend("topright",c("Sent","Received"), col=c("Red","Blue"), lty=1)
title("Number of interactions with other users")
#sort frame by message length to see who got the longest messages
sorted=data[order(data$msglength, decreasing=TRUE),]

# #sent messages by user
usersent <- data[data$senderid == uid,]
sortedUserSent = usersent[order(usersent$msglength, decreasing=TRUE),]
#histogram of user sent messages
plot(sort(table(usersent$receiverid),decreasing=TRUE)[1:10], xaxt="n",xlab="users",ylab="# of messages",t='h',lwd=20)
axis(1,at=1:10,labels=substring(names(sort(table(usersent$receiverid),decreasing=TRUE)[1:10]),1,4),las=2)
title("Top 10 users who received most messages")

plot(sort(table(usersent$receiverid),decreasing=TRUE)[1:10], xaxt="n",xlab="users",ylab="# of messages",t='h',lwd=20)
# user received messages
userrec <- data[data$senderid != uid,]
sortedUserRec = userrec[order(userrec$msglength, decreasing=TRUE),]
#histogram of user received messages
plot(sort(table(userrec$senderid),decreasing=TRUE)[1:10], xaxt="n",xlab="users",ylab="# of messages",t='h',lwd=20)
axis(1,at=1:10,labels=substring(names(sort(table(userrec$senderid),decreasing=TRUE)[1:10]),1,4),las=2)
title("Top 10 users who sent the most messages")


#a plot of number of sent and received messages for alice
plot(table(cut(userrec$date,breaks="week")),type="l",col="Blue", xlab="Weeks",ylab="# of Messages", lty=1)
points(table(cut(usersent$date,breaks="week")), col="Red",type="l")
points(table(cut(usersent$date,breaks="week")), col="Red",type="h")
legend("topright",c("Sent","Received"), col=c("Red","Blue"),lty=c(1,1))
title("Number of messages sent and received by 6617")




#plot messages by user
poi=names(trec[1:6])
plotPerson = function(user, color, marker)
  {
    udata = data[((data$senderid == user) | (data$receiverid == user)),]
    points(udata$date, udata$msglength, col=color, pch=marker)
  }
plot(usersent$date, usersent$msglength, col="black", pch=4, xlab="Time", ylab="Message Length")
plotPerson(poi[2], "blue", 0)
plotPerson(poi[3], "green", 1)
plotPerson(poi[4], "magenta", 11)
plotPerson(poi[5], "yellow", 2)
plotPerson(poi[6], "red", 6)
legend("topright",substring(poi,1,4), col=c("black","Blue","Green","Magenta","Yellow","red"),pch=c(4,0,1,11,2,6))
title("Messages sent by 6617 and top 5 receivers messages (sent/received)")

#bob,carole,dan data frame
## bobdata = data[((data$senderid == bobid) | (data$receiverid == bobid)),]
## caroledata = data[((data$senderid == caroleid) | (data$receiverid == caroleid)),]
## dandata = data[((data$senderid == danid) | (data$receiverid == danid)),]
## #plot data over time 
## plot(data$date, data$msglength)
## #color Bob points red
## points(bobdata$date, bobdata$msglength, col="Blue", pch=0)
## points(caroledata$date, caroledata$msglength, col="Red", pch=2)
## points(dandata$date, dandata$msglength, col="Green", pch=3)
## points(usersent$date, usersent$msglength, col="Magenta", pch=5)
## #distribution of messages over receivers
## barchart(table(usersent$receiverid))
## #messages sent over time
## plot(usersent$date, usersent$msglength)


## #user sent more or received more?
## usent <- length(data$senderid[data$senderid == uid])
## urec <- length(data$receiverid[data$receiverid == uid])
## #received messages by user
## userrec <- data[data$senderid != uid,]
## plot(userrec$date, userrec$msglength)

## #messages over time (blue is sent, red is received)


## plot(usersent$date, usersent$msglength, col="blue")
## axis.Date(1, at=seq(as.Date("2008/10/17"), max(usersent$date)+6, "weeks"))
## points(userrec$date, userrec$msglength, col="red")
## ###############################################
## t=tapply(X=usersent$msglength, INDEX=list(usersent$receiverid),FUN=sum)

## b=by(usersent[,c("msglength")], INDICES=list(usersent$receiverid),FUN=sum)
## a=aggregate(x=usersent[,c("msglength")], by=list(usersent$receiverid),FUN=sum)

## #significant users (msglength over 500)

## ## #filter out extreme heights)
## ## d <- data[data$height>56,]
## ## d <- d[d$height<247,]
## ## #filter out anyone underage
## ## d <- d[d$age>=18,]
## ## # cut out .001 .999
## ## e <- d[d$height<221.1855,]
## ## e <- d[d$height>91.4580,]
## ## #cut out .01, .99
## ## c <- d[d$height>160.0515,]
## ## c <- c[c$height<214.4860,]
## ## # cut out .25 .75
## ## q <- e[e$height>175.2945,]
## ## q <- q[q$height<185.4564,]
## ## cor(e$age, e$height, use = "everything", method=c("pearson","kendall","spearman"))


## ## d <- d[d$height<247,]
## ## d <- d[d$height>56,]


