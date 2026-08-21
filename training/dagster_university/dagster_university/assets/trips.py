from datetime import datetime, timedelta
import requests
import os

from dagster_duckdb import DuckDBResource
from dagster import asset
import duckdb
import pandas as pd

from . import constants

@asset
def taxi_trips_file() -> None:
    """
      The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """
    month_to_fetch = '2023-03'
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)


@asset
def taxi_zones_file() -> None:
    """
      The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal.
    """
    raw_taxi_zones = requests.get(
        "https://data.cityofnewyork.us/api/views/755u-8jsi/rows.csv?accessType=DOWNLOAD"
    )

    with open(constants.TAXI_ZONES_FILE_PATH, "wb") as output_file:
        output_file.write(raw_taxi_zones.content)


@asset(
    deps=["taxi_trips_file"]
)
def taxi_trips(database: DuckDBResource) -> None:
    sql_query = """
        create or replace table taxi_trips as (
          select
            VendorID as vendor_id,
            PULocationID as pickup_zone_id,
            DOLocationID as dropoff_zone_id,
            RatecodeID as rate_code_id,
            payment_type as payment_type,
            tpep_dropoff_datetime as dropoff_datetime,
            tpep_pickup_datetime as pickup_datetime,
            trip_distance as trip_distance,
            passenger_count as passenger_count,
            total_amount as total_amount
          from 'data/raw/taxi_trips_2023-03.parquet'
        );
    """

    with database.get_connection() as conn:
        conn.execute(sql_query)


@asset(
    deps=["taxi_zones_file"],
)
def taxi_zones(database: DuckDBResource) -> None:
    """
      The raw taxi zones dataset, loaded into a DuckDB database.
    """

    query = f"""
      create or replace table zones as (
        select
          LocationID as zone_id,
          zone,
          borough,
          the_geom as geometry
        from '{constants.TAXI_ZONES_FILE_PATH}'
      );
    """

    with database.get_connection() as conn:
        conn.execute(query)

@asset(
    deps = ["taxi_trips"]
)
def trips_by_week(database: DuckDBResource) -> None:

    current_date = datetime.strptime("2023-01-01", constants.DATE_FORMAT)
    end_date = datetime.now()

    result = pd.DataFrame()

    while current_date < end_date:
        current_date_str = current_date.strftime(constants.DATE_FORMAT)
        query = f"""
          select
            vendor_id, total_amount, trip_distance, passenger_count
          from trips
          where pickup_datetime >= '{current_date_str}' and pickup_datetime < '{current_date_str}'::date + interval '1 week'
        """

        with database.get_connection() as conn:
            data_for_week = conn.execute(query).fetch_df()

        aggregate = data_for_week.agg({
            "vendor_id": "count",
            "total_amount": "sum",
            "trip_distance": "sum",
            "passenger_count": "sum"
        }).rename({"vendor_id": "num_trips"}).to_frame().T # type: ignore

        aggregate["period"] = current_date

        result = pd.concat([result, aggregate])

        current_date += timedelta(days=7)

    # clean up the formatting of the dataframe
    result['num_trips'] = result['num_trips'].astype(int)
    result['passenger_count'] = result['passenger_count'].astype(int)
    result['total_amount'] = result['total_amount'].round(2).astype(float)
    result['trip_distance'] = result['trip_distance'].round(2).astype(float)
    result = result[["period", "num_trips", "total_amount", "trip_distance", "passenger_count"]]
    result = result.sort_values(by="period")

    result.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)