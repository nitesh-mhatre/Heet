import os
import pandas as pd
from src.groww import ms_to_datetime 

def merge_csv_remove_duplicates(folder_path):
    """Merge CSV files in a folder and remove duplicates based on 'DT'."""
    dfs = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            dfs.append(pd.read_csv(file_path))
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset='DT')
    return merged_df

def merge_with_final(df_merge, output_folder):
    """Merge a DataFrame with the 'final.csv' file in the output folder."""
    final_file_path = os.path.join(output_folder, 'final.csv')
    if os.path.exists(final_file_path):
        df_final = pd.read_csv(final_file_path)
        if 'DT2' in df_final.columns:
            df_final.drop('DT2', axis=1, inplace=True)
        merged_df = pd.concat([df_merge, df_final], ignore_index=True)
        if 'DT' in merged_df.columns:
            merged_df = merged_df.drop_duplicates(subset='DT')
        return merged_df
    else:
        print(f"'final.csv' does not exist in the folder: {output_folder}")
        return df_merge

if __name__ == '__main__':
    # Paths
    output_path = 'day_output'
    folder_path = 'data/day_data'
    
    # Step 1: Merge CSV files and remove duplicates
    df = merge_csv_remove_duplicates(folder_path)
    
    # Step 2: Merge with 'final.csv' if it exists
    df2 = merge_with_final(df, output_path)
    
    # Step 3: Add and process the 'DT2' column
    df2['DT2'] = pd.to_datetime(df2['DT'])  # Convert 'DT' to datetime
    df2['DT2'] = (df2['DT2'].astype(int) / 10**6).astype(int)  # Convert to milliseconds
    
    # Step 4: Sort the DataFrame by 'DT2'
    df2 = df2.sort_values(by='DT2')
    
    # Step 5: Save the final DataFrame to 'final.csv'
    os.makedirs(output_path, exist_ok=True)
    final_file_path = os.path.join(output_path, 'final.csv')
    df2.to_csv(final_file_path, index=False)
    
    # Output preview
    print("Processed DataFrame (first 2 rows):")
    print(df2.head(2))
    