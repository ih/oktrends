data = read.table("height.csv", header=TRUE, sep=",")

#filter out extreme heights)
d <- data[data$height>56,]
d <- d[d$height<247,]
#filter out anyone underage
d <- d[d$age>=18,]
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
plot(d$age, d$height)
plot(c$age, c$height)
