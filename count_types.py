from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

def count_types(input_file):
    print(f"Analyzing type distribution in {input_file}...")
    
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("TypeCount") \
        .master("local[*]") \
        .config("spark.driver.memory", "8g") \
        .getOrCreate()
    
    try:
        # Read the parquet file
        df = spark.read.parquet(input_file)
        
        # Count total records
        total_records = df.count()
        print(f"\nTotal records: {total_records:,}")
        
        # Group by type_key and count
        type_counts = df.groupBy("type_key") \
            .agg(count("*").alias("count")) \
            .orderBy(col("count").desc())
        
        # Calculate percentages and display results
        print("\nType distribution:")
        print("=" * 80)
        print(f"{'Type Key':<40} {'Count':>12} {'Percentage':>12}")
        print("-" * 80)
        
        type_counts_collected = type_counts.collect()
        for row in type_counts_collected:
            percentage = (row['count'] / total_records) * 100
            print(f"{row['type_key']:<40} {row['count']:>12,} {percentage:>11.2f}%")
        
        print("=" * 80)
        
    finally:
        spark.stop()

if __name__ == "__main__":
    count_types('alltypes_dump.parquet') 