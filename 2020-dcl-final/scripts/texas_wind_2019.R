# Description
# Reading in hourly wind data for Texas
# Source: http://www.ercot.com/gridinfo/generation

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
YEAR <- 2019

# raw aggregate data path
path <- 
  here::here(str_glue(
    "c01-own/data-raw/rpt.00013424.0000000000000000.ERCOT_{YEAR}_Hourly_Wind_Output.xlsx")
  )

# New variable names

vars_rename <- 
  c(
    date_time = "time-date stamp",
    date = "Date",
    load_MW = "ERCOT Load, MW",
    wind_output_MW = "Total Wind Output, MW",
    wind_capacity_MW = "Total Wind Installed, MW",
    wind_output_percent_load = "Wind Output, % of Load",
    wind_output_percent_installed = "Wind Output, % of Installed",
    change_MW = "1-hr MW change",
    change_percent = "1-hr % change"
  )

# Output file with aggregate data in RDS format
file_aggregate_rds <- 
  here::here(str_glue("c01-own/data/texas_wind_{YEAR}.rds"))

#===============================================================================

path %>%
  read_xlsx(sheet = "numbers") %>%
  rename(!!! vars_rename) %>%
  select(
    date_time, 
    wind_capacity_MW, 
    wind_output_percent_load,
    wind_output_percent_installed
  ) %>%
  write_rds(file_aggregate_rds)
