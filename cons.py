import os
import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
RAW_DATA_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_FILE = "consolidated_soil_data.csv"

def consolidate_data():
    all_data = []
    
    # Traverse directory structure
    for year_dir in Path(RAW_DATA_DIR).iterdir():
        if not year_dir.is_dir(): continue
        
        for state_dir in year_dir.iterdir():
            if not state_dir.is_dir(): continue
            
            for district_dir in state_dir.iterdir():
                if not district_dir.is_dir(): continue
                
                # Process files in district directory
                for file in district_dir.glob("*.csv"):
                    # Extract components from file path
                    parts = file.parts
                    year = parts[-4]
                    state = parts[-3]
                    district = parts[-2]
                    block = file.stem.split('_')[0]  # Extract block name from filename
                    
                    # Read and preprocess data
                    df = pd.read_csv(file)
                    
                    # Add geographical metadata
                    df = df.assign(
                        Year=year,
                        State=state,
                        District=district,
                        Block=block,
                        Nutrient_Type="Macro" if "macro" in file.name.lower() else "Micro"
                    )
                    
                    # Standardize column names
                    df.columns = (
                        df.columns.str.strip()
                        .str.lower()
                        .str.replace('[^a-z0-9]', '_', regex=True)
                    )
                    
                    all_data.append(df)
    
    if not all_data:
        raise ValueError("No data files found")
    
    # Combine all datasets
    consolidated = pd.concat(all_data, ignore_index=True)
    
    # Handle missing values
    for col in consolidated.select_dtypes(include=np.number).columns:
        consolidated[col] = consolidated.groupby(
            ['state', 'district', 'block', 'nutrient_type']
        )[col].transform(lambda x: x.fillna(x.median()))
    
    # Standardize data types
    str_cols = ['state', 'district', 'block', 'nutrient_type']
    consolidated[str_cols] = consolidated[str_cols].astype('category')
    
    # Save processed data
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    consolidated.to_csv(f"{PROCESSED_DIR}/{OUTPUT_FILE}", index=False)
    print(f"Consolidated data saved to {PROCESSED_DIR}/{OUTPUT_FILE}")
    return consolidated

if __name__ == "__main__":
    consolidate_data()