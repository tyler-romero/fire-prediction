library(ggplot2)
library(data.table)
library(dplyr)

#Combine data years 2009-2015
df <- read.csv("incidents2009.csv")
tempdf <- read.csv("incidents2010.csv")
df <- bind_rows(df, tempdf)
tempdf <- read.csv("incidents2011.csv")
df <- bind_rows(df, tempdf)
tempdf <- read.csv("incidents2012.csv")
df <- bind_rows(df, tempdf)
tempdf <- read.csv("incidents2013.csv")
df <- bind_rows(df, tempdf)
tempdf <- read.csv("incidents2014.csv")
df <- bind_rows(df, tempdf)
tempdf <- read.csv("incidents2015.csv")
df <- bind_rows(df, tempdf)

df <- filter(df, Call_Category != "")

zipcodes <- df %>% group_by(Postal_Code) %>% summarise(count = n()) %>% filter(count > 4000, Postal_Code != "")
zipcodes <- arrange(zipcodes, desc(count))


temp <- as.POSIXlt(df$PhonePickUp, format = "%m/%d/%y %T")
df$DateTime <- temp
df$Weekday <- wday(df$DateTime)
df$HourOfDay <- hour(df$DateTime)
df$Month <- df$DateTime$mon + 1
df$Year <- df$DateTime$year + 1900


bar2 <- ggplot(df, aes(Weekday, fill = Call_Category)) +
  geom_bar() + 
  ggtitle("Emergency Calls Per Weekday in San Diego, 2009-2015")
print(bar2)

bar3 <- ggplot(df, aes(HourOfDay, fill = Call_Category)) +
  geom_bar() + 
  ggtitle("Emergency Calls Per Hour in San Diego, 2009-2015")
print(bar3)

bar4 <- ggplot(zipcodes, aes(Postal_Code, count)) +
  geom_bar(stat="identity") + 
  ggtitle("Emergency Calls Per Postal Code in San Diego, 2009-2015") +
  theme(axis.text.x  = element_text(angle=90, vjust=0.5, size=9))
print(bar4)

bar5 <- ggplot(df, aes(Month, fill = Call_Category)) +
  geom_bar() + 
  ggtitle("Emergency Calls Per Month in San Diego, 2009-2015")
print(bar5)

bar6 <- ggplot(df, aes(Year, fill = Call_Category)) +
  geom_bar() + 
  ggtitle("Emergency Calls Per Year in San Diego, 2009-2015")
print(bar6)


