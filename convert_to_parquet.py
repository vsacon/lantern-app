from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, schema_of_json
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, ArrayType
import json
import gzip

def convert_to_parquet(input_file, output_file):
    print(f"Converting {input_file} to parquet format...")
    
    # Initialize Spark session with more memory and configuration
    spark = SparkSession.builder \
        .appName("JsonToParquet") \
        .master("local[*]") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "8g") \
        .config("spark.driver.maxResultSize", "4g") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()
    
    try:
        # Read the first line to get a sample of the JSON data
        print("\nReading first line to infer JSON schema...")
        with gzip.open(input_file, 'rt', encoding='utf-8') as f:
            first_line = f.readline().strip()
            columns = first_line.split('\t')
            json_data = columns[4]  # The JSON is in the 5th column
            print("Sample JSON data:", json_data[:200], "...")
            
        # Parse the sample JSON to infer schema
        json_schema = spark.read.json(
            spark.sparkContext.parallelize([json_data])
        ).schema
        
        print("\nInferred JSON Schema:")
        print(json_schema.simpleString())
        
        # Read the TSV file
        print("\nReading complete file...")
        raw_df = spark.read.csv(
            input_file,
            sep='\t',
            header=False,
            inferSchema=False
        ).toDF("type_key", "entity_key", "file_revision", "timestamp", "json_data")
        
        # Parse the JSON column
        parsed_df = raw_df.select(
            col("type_key"),
            col("entity_key"),
            col("file_revision").cast(IntegerType()),
            col("timestamp").cast(TimestampType()),
            from_json(col("json_data"), json_schema).alias("parsed_data")
        )
        
        # Extract type.key for partitioning and flatten the parsed data
        df = parsed_df.select(
            col("type_key"),
            col("entity_key"),
            col("file_revision"),
            col("timestamp"),
            col("parsed_data.created").alias("created"),
            col("parsed_data.key").alias("key"),
            col("parsed_data.last_modified").alias("last_modified"),
            col("parsed_data.latest_revision").alias("latest_revision"),
            col("parsed_data.name").alias("name"),
            col("parsed_data.revision").alias("entity_revision"),
            col("parsed_data.source_records").alias("source_records"),
            col("parsed_data.type").alias("type"),
            col("parsed_data.type.key").alias("entity_type")
        )
        
        # Cache the DataFrame
        df.cache()
        
        print("\nFinal DataFrame Schema:")
        df.printSchema()
        
        record_count = df.count()
        print(f"\nTotal records: {record_count:,}")
        
        print("\nSample of data:")
        df.show(5, truncate=False)
        
        # Save as parquet with partitioning if the dataset is large
        print(f"\nSaving to parquet file: {output_file}")
        try:
            if record_count > 1000000:  # If more than 1M rows, use partitioning
                print("Large dataset detected, using partitioned write...")
                df.write \
                    .option("compression", "snappy") \
                    .mode("overwrite") \
                    .partitionBy("entity_type") \
                    .parquet(output_file)
            else:
                df.write \
                    .option("compression", "snappy") \
                    .mode("overwrite") \
                    .parquet(output_file)
            
            # Verify the save was successful
            print("Verifying saved parquet file...")
            verification_df = spark.read.parquet(output_file)
            saved_count = verification_df.count()
            print(f"Successfully saved {saved_count:,} records to parquet")
            
            if saved_count != record_count:
                print("WARNING: Record count mismatch in saved file!")
            
            # Show sample of the saved data
            print("\nSample of converted data:")
            verification_df.show(5, truncate=False)
            
        except Exception as save_error:
            print(f"Error saving to parquet: {str(save_error)}")
            raise
            
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        raise
    finally:
        # Cleanup
        if 'df' in locals():
            df.unpersist()
        spark.stop()

if __name__ == "__main__":
    try:
        convert_to_parquet(
            input_file='/content/drive/MyDrive/Colab Notebooks/alltypes_dump_temp.txt.gz',
            output_file='/content/drive/MyDrive/Colab Notebooks/alltypes_dump.parquet'
        )
    except Exception as e:
        print(f"Failed to convert file: {str(e)}")
        exit(1) 