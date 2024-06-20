# Description
# Reading in Texas balancing authority data from EIA
# Source: 
# https://www.eia.gov/beta/electricity/gridmonitor/dashboard/electric_overview/balancing_authority/ERCO

# Author: Amy Kouch
# Version: 2020-03-08

# Libraries
library(tidyverse)
library(vroom)
library(utils)
library(readxl)
library(here)

# Parameters

vars_rename_texas <- 
  c(
    region = "Region",
    time = "UTC Time",
    date = "Date",
    local_time = "Local Time",
    time_zone = "Time Zone",
    demand_forecast = "DF",
    demand = "D",
    net_generation = "NG",
    total_interchange = "TI",
    sum_net_generation = "Sum (NG)",
    coal = "NG: COL",
    natural_gas = "NG: NG",
    nuclear = "NG: NUC",
    oil = "NG: OIL",
    hydro = "NG: WAT",
    solar = "NG: SUN",
    wind = "NG: WND",
    other = "NG: OTH",
    unknown = "NG: UNK"
  )

# raw aggregate data path
file_texas <- 
  here::here(str_glue("c01-own/data-raw/Region_TEX.xlsx"))

# Output file with aggregate data in RDS format
file_aggregate_rds <- here::here(str_glue("c01-own/data/texas_ba.rds"))

#===============================================================================

file_texas %>%
  read_xlsx(guess_max = 40777) %>%
  rename(!!! vars_rename_texas) %>%
  select(region:unknown) %>%
  write_rds(file_aggregate_rds)
