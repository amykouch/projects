# Description
# Joining plants and generators data from EIA (2014-2018)

# Author: Amy Kouch
# Version: 2020-01-30

# Libraries
library(tidyverse)
library(vroom)
library(utils)
library(sf)

# Parameters

# year
YEAR <- 2016

# Input files from data
file_plants <- here::here(str_glue("c01-own/data/plants.rds"))
file_generators <- here::here(str_glue("c01-own/data/generators.rds"))

# Output files from data
file_aggregate_rds <- 
  here::here(str_glue("c01-own/data/generators_plants.rds"))

#===============================================================================

plants <- read_rds(file_plants)
generators <- read_rds(file_generators)

generators %>%
  left_join(plants, by = c("plant_code", "year")) %>%
  write_rds(file_aggregate_rds)

