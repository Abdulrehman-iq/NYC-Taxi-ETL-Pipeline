from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, unix_timestamp

def main():
    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("NYC_Taxi_Raw_to_Silver") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # Read CSV from HDFS
    df = spark.read.option("header", "true").csv("hdfs://namenode:9000/user/abdulrehman/raw_data/yellow_tripdata.csv")

    # Convert timestamps
    df = df.withColumn("pickup_datetime", to_timestamp("tpep_pickup_datetime", "MM/dd/yyyy HH:mm:ss")) \
           .withColumn("dropoff_datetime", to_timestamp("tpep_dropoff_datetime", "MM/dd/yyyy HH:mm:ss"))

    # Cast SajCast numeric columns
    numeric_cols = ["passenger_count", "trip_distance", "fare_amount", "tip_amount", "tolls_amount", "total_amount"]
    for col_name in numeric_cols:
        df = df.withColumn(col_name, col(col_name).cast("float"))

    # Filter invalid rows
    df = df.filter(col("trip_distance") > 0) \
           .filter(col("fare_amount") > 0) \
           .filter(col("passenger_count") <= 6)

    # Add trip duration and tip percentage
    df = df.withColumn("trip_duration", (unix_timestamp("dropoff_datetime") - unix_timestamp("pickup_datetime")) / 60) \
           .withColumn("tip_percentage", (col("tip_amount") / col("fare_amount")) * 100)

    # Drop original timestamp columns
    df = df.drop("tpep_pickup_datetime", "tpep_dropoff_datetime")

    # Write to HDFS as Parquet
    df.write.mode("overwrite").parquet("hdfs://namenode:9000/user/abdulrehman/silver_data/yellow_tripdata.parquet")

    spark.stop()

def run_etl():
    """
    ETL function to be called by Airflow DAG
    """
    main()

if __name__ == "__main__":
    main()