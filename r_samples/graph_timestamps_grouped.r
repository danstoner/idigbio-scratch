# Group the data in Postgresql SQL query to reduce the number of data points.
# csv is generated via
# 
# COPY (select date_trunc('day',date_modified),count(*) from idb_object_keys WHERE  user_uuid = '285a4be0-5cfe-4d4f-9c8b-b0f0f3571079' group by date_trunc order by date_trunc)  to '/tmp/uploadsbyday20140909.csv' with CSV;

# 
png(filename="output_uploads_per_day_grouped.png",width=800)
uploads <- read.csv('uploadsbyday20140909.csv', header=FALSE)

barplot(uploads$V2)

#### from other example
# change margins
#par(mai=c(.75,.1,.5,.5))

#uploadstamps <- c(as.POSIXlt (strftime(uploads$V2)) )

#myhist <- hist(uploadstamps,breaks="days",main="Upload events per day",xlab="",ylab="",las=2,xaxt="n",yaxt="n",col="darkgrey",freq=TRUE)

#axis.POSIXct(1, at=seq((uploadstamps[1]-86400), as.POSIXlt(Sys.time()), by="day"), format="%b %d", srt=45, las=2,cex.axis=0.7)

#axis(4, at=myhist$freq)
####

box()
dev.off()