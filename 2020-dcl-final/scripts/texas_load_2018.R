# Description
# Reading in hourly load profile
# Source: http://www.ercot.com/gridinfo/load/load_hist

# Author: Amy Kouch
# Version: 2020-03-08

# Libraries
library(tidyverse)
library(vroom)
library(utils)
library(readxl)
library(here)
library(lubridate)

# Parameters

# year
YEAR <- 2018

# raw aggregate data path
path <- 
  here::here(str_glue("c01-own/data-raw/Native_Load_{YEAR}.xlsx"))

# Output file with aggregate data in RDS format
file_aggregate_rds <- here::here(str_glue("c01-own/data/texas_load_{YEAR}.rds"))

#===============================================================================

path %>%
  read_excel(col_types = "guess") %>%
  rename_all(str_to_lower) %>%
  mutate(time = mdy_hm(hourending)) %>%
  write_rds(file_aggregate_rds)
