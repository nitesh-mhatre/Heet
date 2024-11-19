import os 
import pandas as pd

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
    if os.path.exists(final_file_path):
        df_final = pd.read_csv(final_file_path)
        merged_df = pd.concat([df_merge, df_final], ignore_index=True)
        if 'DT' in merged_df.columns:
            merged_df = merged_df.drop_duplicates(subset='DT')
        
        return merged_df
    else:
        print(f"'final.csv' does not exist in the folder: {output_folder}")
        return merged_df
     
if __name__ == '__main__':
  output_path = 'day_output'
  folder_path = 'data/day_data'
  df = merge_csv_remove_duplicates(folder_path)
  df2 = merge_with_final(df_merge, output_folder)
  df2.to_csv(os.path.join(output_path,'final.csv' ))