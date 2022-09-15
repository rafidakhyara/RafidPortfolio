## ----setup, include=FALSE------------------------------------------------------------------------
knitr::opts_chunk$set(echo = TRUE)


## ----message=FALSE,warning=FALSE-----------------------------------------------------------------
# Note: this process could take a couple of minutes

if(!require(tidyverse)) install.packages("tidyverse", repos = "http://cran.us.r-project.org")
if(!require(caret)) install.packages("caret", repos = "http://cran.us.r-project.org")
if(!require(data.table)) install.packages("data.table", repos = "http://cran.us.r-project.org")
if(!require(dplyr)) install.packages("dplyr")
if(!require(ggplot2)) install.packages("ggplot2")
if(!require(tidyr)) install.packages("tidyr")

library(tidyverse)
library(caret)
library(data.table)
library(dplyr)
library(ggplot2)
library(tidyr)

# MovieLens 10M dataset:
# https://grouplens.org/datasets/movielens/10m/
# http://files.grouplens.org/datasets/movielens/ml-10m.zip

dl <- tempfile()
download.file("http://files.grouplens.org/datasets/movielens/ml-10m.zip", dl)

ratings <- fread(text = gsub("::", "\t", readLines(unzip(dl, "ml-10M100K/ratings.dat"))),
                 col.names = c("userId", "movieId", "rating", "timestamp"))

movies <- str_split_fixed(readLines(unzip(dl, "ml-10M100K/movies.dat")), "\\::", 3)
colnames(movies) <- c("movieId", "title", "genres")

# if using R 4.0 or later:
movies <- as.data.frame(movies) %>% mutate(movieId = as.numeric(movieId),
                                           title = as.character(title),
                                           genres = as.character(genres))

movielens <- left_join(ratings, movies, by = "movieId")

# Validation set will be 10% of MovieLens data
set.seed(1, sample.kind="Rounding") 
test_index <- createDataPartition(y = movielens$rating, times = 1, p = 0.1, list = FALSE)
edx <- movielens[-test_index,]
temp <- movielens[test_index,]

# Make sure userId and movieId in validation set are also in edx set
validation <- temp %>% 
  semi_join(edx, by = "movieId") %>%
  semi_join(edx, by = "userId")

# Add rows removed from validation set back into edx set
removed <- anti_join(temp, validation)
edx <- rbind(edx, removed)


## ------------------------------------------------------------------------------------------------
mu <- mean(edx$rating) 


## ------------------------------------------------------------------------------------------------
#Visualizing movie effect
edx %>% 
  group_by(movieId) %>% 
  summarize(mean = mean(rating)) %>% 
  ggplot(aes(mean)) + 
  geom_histogram(bins = 30)


## ------------------------------------------------------------------------------------------------
#Visualizing user effect
edx %>% 
  group_by(userId) %>% 
  summarize(mean = mean(rating)) %>% 
  ggplot(aes(mean)) + 
  geom_histogram(bins = 30)


## ------------------------------------------------------------------------------------------------
#Visualizing timestamp effect

edx %>% 
  group_by(timestamp) %>% 
  summarize(mean = mean(rating)) %>% 
  ggplot(aes(mean)) + 
  geom_histogram(bins = 30)

tscheck <- edx %>% 
  group_by(timestamp) %>% 
  summarize(mean = mean(rating), n = n())
mean(tscheck$n)


## ------------------------------------------------------------------------------------------------
#Splitting the genres 
edx_genres_split <- edx %>%
  separate_rows(genres,
                sep = "\\|",
                convert = TRUE)

#Visualizing genre effect
edx_genres_split %>% 
  group_by(genres)%>%
  summarize(mean = mean(rating))%>%
  ggplot()+
  geom_col(aes(genres, mean-mu))


## ------------------------------------------------------------------------------------------------
#Visualizing user's genre preference effect
edx_genres_split %>%
  group_by(genres, userId)%>%
  summarize(mean = mean(rating))%>%
  ggplot(aes(mean)) + 
  geom_histogram(bins = 30)


## ------------------------------------------------------------------------------------------------
#Defining the RMSE function
rmse <- function(true_ratings, predicted_ratings) {
  sqrt(mean((true_ratings - predicted_ratings)^2))
}

#Splitting genres in the test set
temp_genres_split <- temp %>%
  separate_rows(genres,
                sep = "\\|",
                convert = TRUE)


## ------------------------------------------------------------------------------------------------
#Effect of user
u_avgs <- edx %>% 
  group_by(userId) %>% 
  summarize(b_u = mean(rating - mu))

#Effect of movies
m_avgs <- edx %>% 
  left_join(u_avgs, by = "userId")%>%
  group_by(movieId) %>% 
  summarize(b_i = mean(rating - mu - b_u))

#Effect of Genres
gs_avgs <- edx_genres_split %>%
  left_join(m_avgs, by = "movieId") %>%
  left_join(u_avgs, by = "userId") %>%
  group_by(genres) %>%
  summarize(b_gs = mean(rating - mu - b_i - b_u))

#Effect of users' genre preferences
gu_avgs <- edx_genres_split %>%
  left_join(m_avgs, by = "movieId") %>%
  left_join(u_avgs, by = "userId") %>%
  left_join(gs_avgs, by = "genres") %>%
  group_by(genres, userId) %>%
  summarize(b_gu = mean(rating - mu - b_i - b_u - b_gs))

#User Effect
predicted_ratings1 <- temp %>% 
  left_join(u_avgs, by='userId') %>%
  mutate(
    b_u = ifelse(is.na(b_u), 0, b_u),
    pred = mu + b_u) %>%
  .$pred
rmse_results <- data.frame(Method = "User Effect", RMSE = rmse(predicted_ratings1, temp$rating))

#User + Movie Effect
predicted_ratings2 <- temp %>% 
  left_join(m_avgs, by='movieId') %>%
  left_join(u_avgs, by='userId') %>%
  mutate(
    b_u = ifelse(is.na(b_u), 0, b_u),
    b_i = ifelse(is.na(b_i), 0, b_i),
    pred = mu + b_i + b_u) %>%
  .$pred

rmse_results <- bind_rows(rmse_results, 
                          data.frame(Method = "User + Movie Effect", 
                                     RMSE = rmse(predicted_ratings2, temp$rating)))

#User + Movie + Genre Effect
predicted_ratings3 <- temp_genres_split %>% 
  left_join(m_avgs, by='movieId') %>%
  left_join(u_avgs, by='userId') %>%
  left_join(gs_avgs, by = "genres") %>%
  mutate(
    b_u = ifelse(is.na(b_u), 0, b_u),
    b_i = ifelse(is.na(b_i), 0, b_i),
    b_gs = ifelse(is.na(b_gs), 0, b_gs),
    pred = mu + b_i + b_u + b_gs) %>%
  .$pred

rmse_results <- bind_rows(rmse_results, 
                          data.frame(Method = "User + Movie + Genre Effect", 
                                     RMSE = rmse(predicted_ratings3, temp_genres_split$rating)))

#User + Movie + Genre + Genre/User Effect
predicted_ratings4 <- temp_genres_split %>% 
  left_join(m_avgs, by='movieId') %>%
  left_join(u_avgs, by='userId') %>%
  left_join(gs_avgs, by = "genres") %>%
  left_join(gu_avgs, by = c("genres", "userId")) %>%
  mutate(
    b_u = ifelse(is.na(b_u), 0, b_u),
    b_i = ifelse(is.na(b_i), 0, b_i),
    b_gs = ifelse(is.na(b_gs), 0, b_gs),
    b_gu = ifelse(is.na(b_gu), 0, b_gu),
    pred = mu + b_i + b_u + b_gs + b_gu) %>%
  .$pred

rmse_results <- bind_rows(rmse_results, 
                          data.frame(Method = "User + Movie + Genre + Genre/User Effect", 
                                     RMSE = rmse(predicted_ratings4, temp_genres_split$rating)))
rmse_results %>% knitr::kable()


## ----message=FALSE,warning=FALSE-----------------------------------------------------------------
#Creating a vector of lambdas
lambdas <- seq(8, 12, 0.25)

#Partitioning the training set for cross-validation
set.seed(1, sample.kind="Rounding")
test_indexcv <- createDataPartition(y = edx$rating, 
                                    times = 1, 
                                    p = 0.2, 
                                    list = FALSE)

edxcv <- edx[-test_indexcv,]
tempcv <- edx[test_indexcv,]

#Splitting genres for these sets
edx_genres_splitcv <- edxcv %>%
  separate_rows(genres,
                sep = "\\|",
                convert = TRUE)

temp_genres_splitcv <- tempcv %>%
  separate_rows(genres,
                sep = "\\|",
                convert = TRUE)

#Running the cross-validation to determine the optimum lambda
cvrmse <- sapply(lambdas, function(l){
  
  #Average of the ratings
  mucv <- mean(edxcv$rating) 
  
  #Effect of user
  u_avgscv <- edxcv %>% 
    group_by(userId) %>% 
    summarize(b_u = (sum(rating - mucv)/ (n() + l)))
  
  #Effect of movies
  m_avgscv <- edxcv %>% 
    left_join(u_avgscv, by = "userId")%>%
    group_by(movieId) %>% 
    summarize(b_i = (sum(rating - mucv - b_u)/ (n() + l)))
  
  #Effect of Genres
  gs_avgscv <- edx_genres_splitcv %>%
    left_join(m_avgscv, by = "movieId") %>%
    left_join(u_avgscv, by = "userId") %>%
    group_by(genres) %>%
    summarize(b_gs = (sum(rating - mucv - b_i - b_u)/ (n() + l)))
  
  #Effect of users' genre preferences
  gu_avgscv <- edx_genres_splitcv %>%
    left_join(m_avgscv, by = "movieId") %>%
    left_join(u_avgscv, by = "userId") %>%
    left_join(gs_avgscv, by = "genres") %>%
    group_by(genres, userId) %>%
    summarize(b_gu = (sum(rating - mucv - b_i - b_u - b_gs)/ (n() + l)))

  predicted_ratingscv <- temp_genres_splitcv %>% 
    left_join(m_avgscv, by='movieId') %>%
    left_join(u_avgscv, by='userId') %>%
    left_join(gs_avgscv, by = "genres") %>%
    left_join(gu_avgscv, by = c("genres", "userId"))%>%
    mutate(
      b_u = ifelse(is.na(b_u), 0, b_u),
      b_i = ifelse(is.na(b_i), 0, b_i),
      b_gs = ifelse(is.na(b_gs), 0, b_gs),
      b_gu = ifelse(is.na(b_gu), 0, b_gu),
      pred = mucv + b_i + b_u + b_gs + b_gu) %>%
    .$pred
  
  return(rmse(predicted_ratingscv, temp_genres_splitcv$rating))
})
qplot(lambdas,cvrmse)

## ------------------------------------------------------------------------------------------------
lambda <- lambdas[which.min(cvrmse)]
lambda


## ------------------------------------------------------------------------------------------------
#Average of the ratings
mu <- mean(edx$rating) 
    
#Effect of user
u_avgs <- edx %>% 
  group_by(userId) %>% 
  summarize(b_u = (sum(rating - mu)/ (n() + lambda)))
    
#Effect of movies
m_avgs <- edx %>% 
  left_join(u_avgs, by = "userId")%>%
  group_by(movieId) %>% 
  summarize(b_i = (sum(rating - mu - b_u)/ (n() + lambda)))
    
#Effect of Genres
gs_avgs <- edx_genres_split %>%
  left_join(m_avgs, by = "movieId") %>%
  left_join(u_avgs, by = "userId") %>%
  group_by(genres) %>%
  summarize(b_gs = (sum(rating - mu - b_i - b_u)/ (n() + lambda)))

    
#Effect of users' genre preferences
gu_avgs <- edx_genres_split %>%
  left_join(m_avgs, by = "movieId") %>%
  left_join(u_avgs, by = "userId") %>%
  left_join(gs_avgs, by = "genres") %>%
  group_by(genres, userId) %>%
  summarize(b_gu = (sum(rating - mu - b_i - b_u - b_gs)/ (n() + lambda)))

# Regularized User + Movie + Genre + Genre/User Effect
predicted_ratings <- temp_genres_split %>% 
  left_join(m_avgs, by='movieId') %>%
  left_join(u_avgs, by='userId') %>%
  left_join(gs_avgs, by = "genres") %>%
  left_join(gu_avgs, by = c("genres", "userId"))%>%
  mutate(
      b_u = ifelse(is.na(b_u), 0, b_u),
      b_i = ifelse(is.na(b_i), 0, b_i),
      b_gs = ifelse(is.na(b_gs), 0, b_gs),
      b_gu = ifelse(is.na(b_gu), 0, b_gu),
      pred = mu + b_i + b_u + b_gs + b_gu) %>%
  .$pred

rmse_results <- bind_rows(rmse_results, 
                               data_frame(Method = "Regularized User + Movie + Genre + Genre/User                                 Effect", 
                                RMSE = rmse(predicted_ratings, temp_genres_split$rating)))
rmse_results %>% knitr::kable()

