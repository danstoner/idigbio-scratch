# csv is generated from Postgresql via
# copy (select etag,date_modified from idb_object_keys where user_uuid = '285a4be0-...' order by date_modified ASC) to '/tmp/uploads20140902.csv' with CSV;
 

# 
uploads <- read.csv('uploads20140902.csv', header=FALSE)

uploadstamps <- c(as.POSIXlt (strftime(uploads$V2)) )

myhist <- hist(uploadstamps,breaks="days",main="Upload events per day",xlab="Date",ylab="",las=2,xaxt="n",yaxt="n",freq=TRUE)

axis.POSIXct(1, at=seq((uploadstamps[1]-86400), as.POSIXlt(Sys.time()), by="day"), format="%b %d", srt=45, las=2,cex.axis=0.7)

axis(4, at=myhist$freq)
