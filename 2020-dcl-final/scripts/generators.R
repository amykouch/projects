# Description
# Reading in generators data from EIA dataset (2014-2018)
# Source: https://www.eia.gov/electricity/data/eia860/

# Author: Amy Kouch
# Version: 2020-03-08

# Libraries
library(tidyverse)
library(vroom)
library(utils)
library(readxl)
library(here)
library(purrr)

# Parameters

# Years
year <- c(2014, 2015, 2016, 2017, 2018)

# New variable names

vars_rename <- 
  c(
    utility_id = "Utility ID",
    utility_name = "Utility Name",
    plant_code = "Plant Code",
    plant_name = "Plant Name",
    state = "State",
    technology = "Technology",
    capacity = "Nameplate Capacity (MW)"
  )

# Output file with aggregate data in RDS format
file_aggregate_rds_gen <- here::here(str_glue("c01-own/data/generators.rds"))

#===============================================================================

generators_df <- function(year) {

  path <- 
    here::here(str_glue("c01-own/data-raw/eia860{year}/3_1_Generator_Y{year}.xlsx"))
 
  file_aggregate_rds <- 
    here::here(str_glue("c01-own/data/generators_{year}.rds")) 
  
  path %>%
    read_excel(skip = 1, col_types = "guess") %>%
    rename(!!! vars_rename) %>%
    select(
      plant_code, 
      state,
      technology, 
      capacity
    ) %>%
    filter(!state %in% c("HI", "AK")) %>%
    mutate(year = {{year}}) %>%
    write_rds(file_aggregate_rds)
}

year %>%
  map_dfr(generators_df) %>%
  write_rds(file_aggregate_rds_gen)
