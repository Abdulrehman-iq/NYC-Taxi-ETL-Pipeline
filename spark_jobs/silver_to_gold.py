from pyspark.sql import SparkSession
from pyspark.sql.functions import col,to_date,hour,avg,sum as _sum,count

def main():
    spark=SparkSession.builder \
        .appName("NYC_Taxi_Silver_to_Gold") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .config("spark.jars","path/to/postgresql.jar" )\
        .getOrCreate()
    
    silver_df = spark.read.parquet("hdfs://namenode:9000/user/abdulrehman/silver_data/yellow_tripdata.parquet")

    enriched =silver_df\
        .withColumn("pickup_date",to_date("pickup_datetime"))\
        .withColumn("pickup_hour",hour("pickup_datetime"))
    
    gold_df= enriched.groupBy("pickup_date","pickup_hour")\
        .agg(
            _sum("trip_distance").alias("total_distance"),
            _sum("fare_amount").alias("total_fare"),
            _sum("tip_amount").alias("total_tips"),
            avg("trip_duration").alias("avg_duration"),
            avg("tip_percentage").alias("avg_tip_percentage"),
            count("*").alias("total_trips")
        )
  
    gold_df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://db_host:5432/rideflow") \
    .option("dbtable", "public.gold_hourly_trips") \
    .option("user", "rideflow_user") \
    .option("password", "postgress") \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()

    spark.stop()

    def run_etl():
        """
        ETL function to be called by Airflow DAG
        """
        main()
if __name__ == "__main__":
    main()