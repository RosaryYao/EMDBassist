# Title     : TODO
# Objective : Transform Brigg's .motl format (or .csv)
# Created by: Rosary
# Created on: 2020/11/17


args <- commandArgs(trailingOnly = TRUE)
f <- read.csv(args[1], header = FALSE)
f_t <- t(f)

if (length(args)==1) {args[2] <- "output.csv"}

write.table(f_t, args[2], row.names = FALSE, col.names = FALSE, sep=",")









