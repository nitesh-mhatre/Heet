import os 
import pandas as pd

output_path = 'day_output'
folder_path = 'data/day_data'

def merge_csv_remove_duplicates(folder_path):
    dfs = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            dfs.append(pd.read_csv(file_path))
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset='DT')
    return merged_df

def merge_with_final(df_merge, output_folder):
    
    final_file_path = os.path.join(output_folder, 'final.csv')
    
    # Check if 'final.csv' exists
    if os.path.exists(final_file_path):
        # Load 'final.csv' into a DataFrame
        df_final = pd.read_csv(final_file_path)
        
        # Merge the two DataFrames (outer join to include all data, change as needed)
        merged_df = pd.concat([df_merge, df_final], ignore_index=True)
        
        # Optionally, remove duplicates (e.g., based on 'DT' column if required)
        if 'DT' in merged_df.columns:
            merged_df = merged_df.drop_duplicates(subset='DT')
        
        return merged_df
    else:
        # Do nothing if 'final.csv' does not exist
        print(f"'final.csv' does not exist in the folder: {output_folder}")
        return merged_df
