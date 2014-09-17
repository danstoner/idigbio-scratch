# csv is generated from Postgresql via
# copy (select etag,date_modified from idb_object_keys where user_uuid = '285a4be0-...' order by date_modified ASC) to '/tmp/uploads20140902.csv' with CSV;
 

# 
png(filename="output_uploads_per_day.png",width=800)
uploads <- read.csv('uploads20140917.csv', header=FALSE)

# change margins
par(mai=c(.75,.1,.5,.5))

uploadstamps <- c(as.POSIXlt (strftime(uploads$V2)) )

myhist <- hist(uploadstamps,breaks="days",main="Upload events per day",xlab="",ylab="",las=2,xaxt="n",yaxt="n",col="darkgrey",freq=TRUE)

axis.POSIXct(1, at=seq((uploadstamps[1]-86400), as.POSIXlt(Sys.time()), by="day"), format="%b %d", srt=45, las=2,cex.axis=0.7)

axis(4, at=myhist$freq)
box()
dev.off()