import os

from pyspark.sql import SparkSession

script_dir = os.path.dirname(__file__)
input_file_path = os.path.join(script_dir, 'input.csv')


def orchestrator():
    # Create a Spark session
    spark = SparkSession.builder.appName("PySpark Basics").getOrCreate()

    # Read data from a CSV file into a DataFrame
    df = spark.read.csv(input_file_path, header=True, inferSchema=True)

    # Show the first few rows of the DataFrame
    df.show()

    # Perform some basic transformations
    df_filtered = df.filter(df["age_years"] > 5)
    df_grouped = df_filtered.groupBy("class").count()

    # Show the results
    df_grouped.show()

if __name__ == "__main__":
    orchestrator()