data = read.table("height.csv", header=TRUE, sep=",")

#filter out extreme heights)
d <- data[data$height>56,]
d <- d[d$height<247,]
#filter out anyone underage
d <- d[d$age>=18,]
#convert height to inches (in display convert to feet inches)
d$inches = round(d$height*0.393700787)
#plot the first generation
tdata = table(d[(d$age>22 & d$age<=28),]$inches) #pre-college millenials
t=data.frame(tdata)
t$Var1=as.numeric(names(tdata))
plot(t,type='h',lwd=6, xlab="Height (in feet)", ylab="Frequency", col="red",xaxt="n")
axis(1,at=c(24,36,48,60,72,84,96), labels=c("2","3","4","5","6","7","8"))
#plot(range(60:80),range(0:4000),t='n')
#plotGen(22,28,"black")

plotGen(28,45,"orange") #gen x
plotGen(18,22,"yellow") #college
plotGen(45,55,"green")
plotGen(55,64,"blue")
plotGen(64,82,"magenta")
plotGen(82,88,"violet")
plotGen(88,98,"black")
legend("topleft",c("18-22","23-28","29-45","46-55","56-64","65-82","83-88","88-98"), col=c("yellow","red","orange","green","blue","magenta","violet","black"),lty=1)
title("Distribution of height color-coded by age group")
plotGen = function(lowAge,highAge,color)
  {
    gdata=d[(d$age>lowAge & d$age<=highAge),]
    tdata = table(gdata$inches)
    t=data.frame(tdata)
    t$Var1=as.numeric(names(tdata))
    points(t, col=color, t='h',lwd=6)
#    points(mean(gdata$inches),4000,t='h',lwd=3,col=color)
    mean(gdata$inches)
  }


# cut out .001 .999
e <- d[d$height<221.1855,]
e <- d[d$height>91.4580,]
#cut out .01, .99
c <- d[d$height>160.0515,]
c <- c[c$height<214.4860,]
# cut out .25 .75
q <- e[e$height>175.2945,]
q <- q[q$height<185.4564,]

cor(e$age, e$height, use = "everything", method=c("pearson","kendall","spearman"))


d <- d[d$height<247,]
d <- d[d$height>56,]


#visualization
