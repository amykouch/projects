Wind Energy in Texas
================
Amy Kouch
2019-

``` r
# Libraries
library(tidyverse)
library(readxl)
library(lubridate)

# Parameters

YEAR <- 2018

file_texas_ba <- 
  here::here(str_glue("c01-own/data/texas_ba.rds"))

file_texas_wind <- 
  here::here(str_glue("c01-own/data/wind_generation_{YEAR}.rds"))
```

``` r
texas_ba <-
  file_texas_ba %>%
  read_rds() 
```
