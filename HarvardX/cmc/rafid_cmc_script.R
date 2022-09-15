## ----message=FALSE,warning=FALSE-----------------------------------------------------------------
if(!require(tidyverse)) install.packages("tidyverse", repos = "http://cran.us.r-project.org")
if(!require(caret)) install.packages("caret", repos = "http://cran.us.r-project.org")
if(!require(data.table)) install.packages("data.table", repos = "http://cran.us.r-project.org")
if(!require(dplyr)) install.packages("dplyr")
if(!require(ggplot2)) install.packages("ggplot2")
if(!require(graphics)) install.packages("graphics")
if(!require(gridExtra)) install.packages("gridExtra")
if(!require(glmnet)) install.packages("glmnet")
if(!require(ggpubr)) install.packages("ggpubr")
if(!require(raster)) install.packages("raster")
if(!require(gtools)) install.packages("gtools")

library(ggplot2)
library(dplyr)
library(graphics)
library(gridExtra)
library(caret)
library(glmnet)
library(tidyverse)
library(ggpubr)
library(raster)
library(gtools)

dl <- tempfile()
download.file("https://archive.ics.uci.edu/ml/machine-learning-databases/cmc/cmc.data", dl)

#Downloading and importing the data
cmc <- read.csv(dl)

#Setting the variable names
colnames(cmc) <- c("WIFE_AGE", "WIFE_EDUCATION", "HUSB_EDUCATION",
                   "CHILDREN_NUMBER", "WIFE_RELIGION", 
                   "WIFE_WORKING", "HUSBAND_OCCUPATION", "STANDARD_OF_LIVING",
                   "MEDIA_EXPOSURE", "CONTRACEPTIVE_METHOD_USED")

#Creating the training and test sets
set.seed(1, sample.kind = "Rounding")
testindex <- sample.int(n = nrow(cmc),
                        size = floor(0.3 * nrow(cmc)), 
                        replace = FALSE)
testset <- cmc[testindex,]
trainset <- cmc[-testindex,]

#Setting the variables as characters for visualization purposes
for(x in c(1:10)[-c(1,4)]){
  trainset[,x] <- as.character(trainset[,x])
}

#Converting the numbers in 'CONTRACEPTIVE_METHOD_USED' into labels
trainset$CONTRACEPTIVE_METHOD_USED <- trainset$CONTRACEPTIVE_METHOD_USED %>%
  str_replace_all("1", "No-use") %>%
  str_replace_all("2", "Long-term") %>%
  str_replace_all("3", "Short-term") %>%
  factor(levels = c("No-use", "Short-term", "Long-term"))
  


## ------------------------------------------------------------------------------------------------
#Creating boxplots for age for each type contraceptive
ageplot <- trainset %>%
    ggplot()+
    geom_boxplot(aes(y = WIFE_AGE,
                     fill = CONTRACEPTIVE_METHOD_USED))+
    theme(axis.title.x = element_blank(), 
        axis.text.x = element_blank(), 
        axis.ticks.x = element_blank())
ageplot


## ------------------------------------------------------------------------------------------------
#Creating donut charts for each level of education
weduplot1 <- trainset %>%
  filter(WIFE_EDUCATION == 1) %>%
  ggplot()+
  geom_bar(aes(x = WIFE_EDUCATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

weduplot2 <- trainset %>%
  filter(WIFE_EDUCATION == 2) %>%
  ggplot()+
  geom_bar(aes(x = WIFE_EDUCATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "2",
           size = 5)

weduplot3 <- trainset %>%
  filter(WIFE_EDUCATION == 3) %>%
  ggplot()+
  geom_bar(aes(x = WIFE_EDUCATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "3",
           size = 5)

weduplot4 <- trainset %>%
  filter(WIFE_EDUCATION == 4) %>%
  ggplot(aes(x = WIFE_EDUCATION,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "4",
           size = 5)

#Combining all charts
arrangeGrob(weduplot1, weduplot2,
            weduplot3, weduplot4) %>%
  annotate_figure(top = text_grob("Effect of Women's Education on Contraception Use"),
                  bottom = text_grob("1=low, 2, 3, 4=high",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Creating donut charts for each level of education
heduplot1 <- trainset %>%
  filter(HUSB_EDUCATION == 1) %>%
  ggplot()+
  geom_bar(aes(x = HUSB_EDUCATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

heduplot2 <- trainset %>%
  filter(HUSB_EDUCATION == 2) %>%
  ggplot()+
  geom_bar(aes(x = HUSB_EDUCATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "2",
           size = 5)

heduplot3 <- trainset %>%
  filter(HUSB_EDUCATION == 3) %>%
  ggplot()+
  geom_bar(aes(x = HUSB_EDUCATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "3",
           size = 5)

heduplot4 <- trainset %>%
  filter(HUSB_EDUCATION == 4) %>%
  ggplot(aes(x = HUSB_EDUCATION,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "4",
           size = 5)

#Combining all charts
arrangeGrob(heduplot1, heduplot2,
            heduplot3, heduplot4)%>%
  annotate_figure(top = text_grob("Effect of Husband's Education on Contraception Use"),
                  bottom = text_grob("1=low, 2, 3, 4=high",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Creating boxplots for number of children for each type of contraceptive
childplot <- trainset %>%
  ggplot()+
    geom_boxplot(aes(y = CHILDREN_NUMBER,
                   fill = CONTRACEPTIVE_METHOD_USED))+
    theme(axis.title.x = element_blank(), 
        axis.text.x = element_blank(), 
        axis.ticks.x = element_blank())
childplot


## ------------------------------------------------------------------------------------------------
#Creating donut charts for each religion
religplot1 <- trainset %>%
  filter(WIFE_RELIGION == 1) %>%
  ggplot(aes(x = WIFE_RELIGION,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "0",
           size = 5)

religplot2 <- trainset %>%
  filter(WIFE_RELIGION == 0) %>%
  ggplot(aes(x = WIFE_RELIGION,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

#Combining all charts
arrangeGrob(religplot1, religplot2)%>%
  annotate_figure(top = text_grob("Effect of Wife's Religion on Contraception Use"),
                  bottom = text_grob("0=Non-Islam, 1=Islam",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Creating donut charts for working status
wifeworkplot1 <- trainset %>%
  filter(WIFE_WORKING == 0) %>%
  ggplot(aes(x = WIFE_WORKING,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "0",
           size = 5)

wifeworkplot2 <- trainset %>%
  filter(WIFE_WORKING == 1) %>%
  ggplot(aes(x = WIFE_WORKING,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

#Combining all charts
arrangeGrob(wifeworkplot1, wifeworkplot2)%>%
  annotate_figure(top = text_grob("Effect of Wife's Occupation on Contraception Use"),
                  bottom = text_grob("0=Working, 1=Not working",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Creating donut charts for each category of job
husbworkplot1 <- trainset %>%
  filter(HUSBAND_OCCUPATION == 1) %>%
  ggplot()+
  geom_bar(aes(x = HUSBAND_OCCUPATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

husbworkplot2 <- trainset %>%
  filter(HUSBAND_OCCUPATION == 2) %>%
  ggplot()+
  geom_bar(aes(x = HUSBAND_OCCUPATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "2",
           size = 5)

husbworkplot3 <- trainset %>%
  filter(HUSBAND_OCCUPATION == 3) %>%
  ggplot()+
  geom_bar(aes(x = HUSBAND_OCCUPATION,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "3",
           size = 5)

husbworkplot4 <- trainset %>%
  filter(HUSBAND_OCCUPATION == 4) %>%
  ggplot(aes(x = HUSBAND_OCCUPATION,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "4",
           size = 5)

#Combining all charts
arrangeGrob(husbworkplot1, husbworkplot2,
             husbworkplot3, husbworkplot4)%>%
  annotate_figure(top = text_grob("Effect of Husband's Occupation on Contraception Use"),
                  bottom = text_grob("1, 2, 3, 4 are numbers representing nominal categories of the husband's occupation.",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Creating donut charts for each standard of living index
solplot1 <- trainset %>%
  filter(STANDARD_OF_LIVING == 1) %>%
  ggplot()+
  geom_bar(aes(x = STANDARD_OF_LIVING,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

solplot2 <- trainset %>%
  filter(STANDARD_OF_LIVING == 2) %>%
  ggplot()+
  geom_bar(aes(x = STANDARD_OF_LIVING,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "2",
           size = 5)

solplot3 <- trainset %>%
  filter(STANDARD_OF_LIVING == 3) %>%
  ggplot()+
  geom_bar(aes(x = STANDARD_OF_LIVING,
               fill = CONTRACEPTIVE_METHOD_USED))+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "3",
           size = 5)

solplot4 <- trainset %>%
  filter(STANDARD_OF_LIVING == 4) %>%
  ggplot(aes(x = STANDARD_OF_LIVING,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "4",
           size = 5)

#Combining all charts
arrangeGrob(solplot1, solplot2,
             solplot3, solplot4)%>%
  annotate_figure(top = text_grob("Effect of Standard of Living on Contraception Use"),
                  bottom = text_grob("1=low, 2, 3, 4=high",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Creating donut charts for each level of media exposure
mediaplot1 <- trainset %>%
  filter(MEDIA_EXPOSURE == 0) %>%
  ggplot(aes(x = MEDIA_EXPOSURE,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "0",
           size = 5)

mediaplot2 <- trainset %>%
  filter(MEDIA_EXPOSURE == 1) %>%
  ggplot(aes(x = MEDIA_EXPOSURE,
             fill = CONTRACEPTIVE_METHOD_USED))+
  geom_bar()+
  coord_polar(theta = "y")+
  theme_void()+
  theme(legend.title = element_text(size=8),
        legend.text = element_text(size=8))+
  annotate("text", 
           x = 0, y = 0, 
           label = "1",
           size = 5)

#Combining all charts
arrangeGrob(mediaplot1, mediaplot2)%>%
  annotate_figure(top = text_grob("Effect of Media Exposure on Contraception Use"),
                  bottom = text_grob("0=Good, 1=Not good",
                                     hjust = 1, x = 1, size = 8))


## ------------------------------------------------------------------------------------------------
#Setting to numeric for analysis purposes
trainset$CONTRACEPTIVE_METHOD_USED <- trainset$CONTRACEPTIVE_METHOD_USED %>%
  str_replace_all("No-use", "1") %>%
  str_replace_all("Long-term", "2") %>%
  str_replace_all("Short-term", "3") %>%
  as.factor()

for(n in c(1:10)){
  trainset[,n] <- as.numeric(trainset[,n])
}

#Simulating guessing with corresponding probabilities
set.seed(69, sample.kind = "Rounding")
GUESS <- as.factor(sample(c(1,2,3),
       length(testset$CONTRACEPTIVE_METHOD_USED),
       replace = TRUE,
       prob = c(sum(trainset$CONTRACEPTIVE_METHOD_USED == 1)/length(trainset$CONTRACEPTIVE_METHOD_USED),
                sum(trainset$CONTRACEPTIVE_METHOD_USED == 2)/length(trainset$CONTRACEPTIVE_METHOD_USED),
                sum(trainset$CONTRACEPTIVE_METHOD_USED == 3)/length(trainset$CONTRACEPTIVE_METHOD_USED))))

#Displaying results
data.frame(Model = "Guessing", 
                     Accuracy = confusionMatrix(GUESS, as.factor(testset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"]) %>%
  knitr::kable()



## ------------------------------------------------------------------------------------------------
#Creating a basic linear model.

linear <- lm(CONTRACEPTIVE_METHOD_USED ~ .,
             data = trainset)

predictlm <- as.factor(clamp(round(predict(linear, testset)),1,3))

#Displaying results
accuracy <- data.frame(Model = "Wife's Age + Wife's Education + Husband's Education + Children Number + Wife's Religion + Husband's Occupation + Standard of Living + Media Exposure + Wife Working", 
                     Accuracy = confusionMatrix(predictlm, as.factor(testset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"])
  
accuracy %>% knitr::kable()



## ------------------------------------------------------------------------------------------------
summary(linear)[4]


## ---- message = FALSE, warning = FALSE-----------------------------------------------------------
#Linear model using only significant variables
lineartested <- lm(CONTRACEPTIVE_METHOD_USED ~ WIFE_AGE + WIFE_EDUCATION + CHILDREN_NUMBER + WIFE_RELIGION + STANDARD_OF_LIVING,
                   data = trainset)

predictlm2 <- as.factor(clamp(round(predict(lineartested, testset)),1,3))

#Displaying results
accuracy <- rbind(accuracy,
data.frame(Model = "Tested Linear Model", 
                     Accuracy = confusionMatrix(predictlm2, as.factor(testset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"])
)
  
accuracy %>% knitr::kable()


## ---- message = FALSE, warning = FALSE-----------------------------------------------------------
predictlm3 <- predict(lineartested, testset)

#Creating the permutations
deci <- permutations(length(seq(0,1,0.05)),2,seq(0,1,0.05))

#Finding optimal cut-off point for rounding.
b <- 5

set.seed(69, sample.kind = "Rounding")
bestdeci <- replicate(b,{
  #Creating sub- training and test sets
  testindex <- sample.int(n = nrow(trainset),
                          size = floor(0.3 * nrow(trainset)), 
                          replace = FALSE)
  subtestset <- trainset[testindex,]
  subtrainset <- trainset[-testindex,]
  
  for(n in c(1:10)){
    subtrainset[,n] <- as.numeric(subtrainset[,n])
  }
  
  lineartested <- lm(CONTRACEPTIVE_METHOD_USED ~ WIFE_AGE + WIFE_EDUCATION + CHILDREN_NUMBER + WIFE_RELIGION + STANDARD_OF_LIVING,
                     data = subtrainset)
  
  predictlm3 <- predict(lineartested, subtestset)
  a <- data.frame()
  
  #Testing the cutoff points
  decitest <- sapply(c(1:nrow(deci)),function(x){
    for(n in c(1:length(predictlm3))){
      predictlm3[n] <- ifelse(predictlm3[n]<2-deci[x,1], floor(predictlm3[n]), ifelse(predictlm3[n]>2+deci[x,2], ceiling(predictlm3[n]), 2))
    }
    predictlm3 <- as.factor(clamp(predictlm3,1,3))
    
    a <- rbind(a, data.frame(
      Class_1 = as.numeric(confusionMatrix(predictlm3, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$byClass[1,1]),
      Class_2 = as.numeric(confusionMatrix(predictlm3, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$byClass[2,1]),
      Class_3 = as.numeric(confusionMatrix(predictlm3, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$byClass[3,1]),
      x1 = as.numeric(deci[x,1]),
      x2 = as.numeric(deci[x,2]),
      acc = confusionMatrix(predictlm3, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"]))
  })
  decitest
})

bestdeci <- as.data.frame(t(matrix(bestdeci, 6, 420*b)))

colnames(bestdeci) <- c("C1", "C2", "C3", "X1", "X2", "Acc")

#Determining the best cutoff points
bestdeci <- bestdeci %>%
  mutate(across(.fns = as.numeric)) %>%
  dplyr::group_by(X1,X2) %>%
  summarize(C1bar = mean(C1),
            C2bar = mean(C2),
            C3bar = mean(C3),
            Acc = mean(Acc)) %>%
  filter(C1bar >= 0.4 & C2bar >= 0.4 & C3bar >= 0.4)

predictlm3 <- predict(lineartested, testset)

#Applying cutoff points in rounding procedure
for(n in c(1:length(predictlm3))){
  predictlm3[n] <- ifelse(predictlm3[n]<2-bestdeci$X1[which.max(bestdeci$Acc)], floor(predictlm3[n]), ifelse(predictlm3[n]>2+bestdeci$X2[which.max(bestdeci$Acc)], ceiling(predictlm3[n]), 2))
}

predictlm3 <- as.factor(clamp(predictlm3,1,3))

#Displaying results
accuracy <- rbind(accuracy,
data.frame(Model = "Tested Linear Model, Custom Rounding", 
                     Accuracy = confusionMatrix(predictlm3, as.factor(testset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"])
)

accuracy %>% knitr::kable()


## ----warning=FALSE-------------------------------------------------------------------------------
#Converting to matrix for regularization
matrix_trainset <- as.matrix(trainset)
x <- matrix_trainset[,-c(3,6,7,9,10)]
y <- matrix_trainset[,10]

set.seed(1, sample.kind = "Rounding")
reg <- function(a,b){
  cv.glmnet(a,b, alpha = 0,
            nfolds = 10)
}

regularize <- reg(x,y)

z <- as.matrix(testset)[,-c(3,6,7,9,10)]

predictreg <- predict(regularize, z,
                      s = "lambda.min")

#Same process as above in picking cutoff point
set.seed(69, sample.kind = "Rounding")
bestdecireg <- replicate(b,{
  testindex <- sample.int(n = nrow(trainset),
                          size = floor(0.3 * nrow(trainset)), 
                          replace = FALSE)
  subtestset <- trainset[testindex,]
  subtrainset <- trainset[-testindex,]
  
  for(n in c(1:10)){
    subtrainset[,n] <- as.numeric(subtrainset[,n])
  }
  
  matrix_subtrainset <- as.matrix(subtrainset)
  x <- matrix_subtrainset[,-c(3,6,7,9,10)]
  y <- matrix_subtrainset[,10]
  
  regularize <- reg(x,y)
  
  z <- as.matrix(subtestset)[,-c(3,6,7,9,10)]
  
  predictreg <- predict(regularize, z,
                        s = "lambda.min")
  
  a <- data.frame()
  
  decitest <- sapply(c(1:nrow(deci)),function(x){
    for(n in c(1:length(predictreg))){
      predictreg[n] <- ifelse(predictreg[n]<2-deci[x,1], floor(predictreg[n]), ifelse(predictreg[n]>2+deci[x,2], ceiling(predictreg[n]), 2))
    }
    predictreg <- as.factor(clamp(as.numeric(predictreg), 1, 3))
    
    a <- rbind(a, data.frame(
      Class_1 = as.numeric(confusionMatrix(predictreg, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$byClass[1,1]),
      Class_2 = as.numeric(confusionMatrix(predictreg, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$byClass[2,1]),
      Class_3 = as.numeric(confusionMatrix(predictreg, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$byClass[3,1]),
      x1 = as.numeric(deci[x,1]),
      x2 = as.numeric(deci[x,2]),
      acc = confusionMatrix(predictreg, as.factor(subtestset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"]))
  })
  decitest
})

bestdecireg <- as.data.frame(t(matrix(bestdecireg, 6, 420*b)))

colnames(bestdecireg) <- c("C1", "C2", "C3", "X1", "X2", "Acc")

bestdecireg <- bestdecireg %>%
  mutate(across(.fns = as.numeric)) %>%
  dplyr::group_by(X1,X2) %>%
  summarize(C1bar = mean(C1),
            C2bar = mean(C2),
            C3bar = mean(C3),
            Acc = mean(Acc)) %>%
  filter(C1bar >= 0.4 & C2bar >= 0.4 & C3bar >= 0.4)

predictreg <- predict(lineartested, testset)

for(n in c(1:length(predictreg))){
  predictreg[n] <- ifelse(predictreg[n]<2-bestdecireg$X1[which.max(bestdecireg$Acc)], floor(predictreg[n]), ifelse(predictreg[n]>2+bestdecireg$X2[which.max(bestdecireg$Acc)], ceiling(predictreg[n]), 2))
}

predictreg <- as.factor(clamp(as.numeric(predictreg), 1, 3))


## ------------------------------------------------------------------------------------------------
#Displaying results
accuracy <- rbind(accuracy,
data.frame(Model = "Regularized Tested Linear Model, Custom Rounding", 
                     Accuracy = confusionMatrix(predictreg, as.factor(testset$CONTRACEPTIVE_METHOD_USED))$overall["Accuracy"])
)

accuracy %>% knitr::kable()

