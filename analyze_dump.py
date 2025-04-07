from pyspark.sql import SparkSession
import gzip
import json
from pprint import pprint

def is_likely_header(first_row, second_row):
    """
    Check if the first row is likely a header by comparing it with the second row.
    Returns True if it looks like a header, False otherwise.
    """
    if len(first_row) != len(second_row):
        return False
    
    # Check if first row contains any numeric values
    has_numeric = any(val.replace('.', '').replace('-', '').isdigit() for val in first_row)
    
    # Check if first row elements look like column names
    looks_like_header = all(
        val.replace('_', '').replace(' ', '').isalnum() and  # Contains only alphanumeric chars
        not val.replace('.', '').isdigit() and               # Not purely numeric
        len(val) < 100                                       # Not too long
        for val in first_row
    )
    
    return looks_like_header and not has_numeric

def analyze_first_rows(file_path, num_rows=50):
    print(f"Reading first {num_rows + 1} rows from {file_path}...")
    
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("DumpAnalysis") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    
    try:
        # Read first few rows to analyze structure
        rows = []
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            # Read first two rows to check for header
            first_line = f.readline().strip()
            second_line = f.readline().strip()
            
            first_row = first_line.split('\t')
            second_row = second_line.split('\t')
            
            # Detect if first row is header
            has_header = is_likely_header(first_row, second_row)
            
            if has_header:
                print("\nHeader detected!")
                header = first_row
                rows.append(second_row)  # Add second row as first data row
            else:
                print("\nNo header detected. Using generated column names.")
                header = [f"col_{i}" for i in range(len(first_row))]
                rows.append(first_row)   # Add first row as data
                rows.append(second_row)  # Add second row as data
            
            print("\nColumns found:", len(header))
            print("Column names:", header)
            
            # Read remaining rows
            for _ in range(num_rows - 1):  # -1 because we already read one or two rows
                line = f.readline()
                if not line:
                    break
                row = line.strip().split('\t')
                rows.append(row)
        
        # Create RDD from rows
        rdd = spark.sparkContext.parallelize(rows)
        
        # Create DataFrame with header
        df = rdd.toDF(header)
        
        print("\nDataFrame Schema:")
        df.printSchema()
        
        print("\nDataFrame Info:")
        print(f"Number of rows: {df.count()}")
        print(f"Number of columns: {len(df.columns)}")
        
        # If there's a JSON column, try to parse the first row
        for col in df.columns:
            try:
                json_str = df.select(col).first()[0]
                json_data = json.loads(json_str)
                print(f"\nJSON structure found in column '{col}':")
                pprint(json_data, indent=2)
                break
            except:
                continue
        
        print("\nFirst few rows of data:")
        df.show(5, truncate=False)
        
        return df
        
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None
    finally:
        # Stop Spark session
        spark.stop()

# Use the function
df = analyze_first_rows('alltypes_dump_temp.txt.gz') 