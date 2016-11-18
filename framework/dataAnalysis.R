library(ggplot2)

respTimes <- read.table("responseTimes.txt")

hist1 <- ggplot(respTimes, aes(V1)) +
  geom_histogram(bins=25) +
  xlab("Response Time (min)") +
  ggtitle("Response Time Histogram")
print(hist1)