# Pam's request - 16k+ genera

#install.packages("devtools")
#library(devtools)
#install_github("idigbio/ridigbio")
library(ridigbio)
setwd("~/r_for_pam")

genera <- read.csv("genus.csv", header=TRUE)
field_list <- c("uuid", "genus", "specificepithet", 
              "geopoint.lat", "geopoint.lon", "country", 
              "stateprovince", "county", "municipality")

counter <- 1
df <- FALSE
some_g <- c()
for (g in genera$genus){

  some_g <- c(some_g, g)
 
  
  counter <- counter+1
  if (counter %% 200 == 0) { 
    temp_df <- idig_search_records(rq=list(genus=some_g), fields=field_list)
    typeof(temp_df)
    
    if (nrow(temp_df) != 0 && df != FALSE) {
      df <- rbind(df, temp_df)
    }else if (nrow(temp_df) != 0){
      df <- temp_df
    }
    
    print(sprintf("%d Genus %s, output size %d", counter, some_g[1], nrow(df)))
    # break
    some_g <- c()
  }
}

if (length(some_g) > 0){
  temp_df <- idig_search_records(rq=list(genus=some_g), fields=field_list)
  typeof(temp_df)
  
  if (nrow(temp_df) != 0 && df != FALSE) {
    df <- rbind(df, temp_df)
  }else if (nrow(temp_df) != 0){
    df <- temp_df
  }
}

write.csv(df, file="records.csv")
