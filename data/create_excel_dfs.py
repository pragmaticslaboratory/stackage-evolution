import os
import pandas as pd
import pickle  # For reading/writing custom ".df" files

# Define the input data folder
data_folder = 'dfs'  # Change to your actual data folder name

# Define the output folder where Excel files will be saved
output_folder = 'output_excels'

# Ensure the output folder exists, create it if it doesn't
os.makedirs(output_folder, exist_ok=True)

# Function to read custom ".df" files
def read_df_file(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

# Function to write custom ".df" files
def write_df_file(dataframe, output_path):
    with open(output_path, 'wb') as f:
        pickle.dump(dataframe, f)

# Function to convert DataFrame to Excel
def dataframe_to_excel(dataframe, output_path):
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')  # You can also use 'openpyxl'
    dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()

# Walk through subdirectories in alphabetical order
for root, dirs, files in os.walk(data_folder):
    dirs.sort()  # Sort subdirectories alphabetically
    
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        
        # Process files in the current subdirectory
        for file in os.listdir(dir_path):
            if file.endswith('.df'):  # Adjust the file extension as needed
                file_path = os.path.join(dir_path, file)
                
                # Read the custom ".df" file into a Pandas DataFrame
                df = read_df_file(file_path)
                
                # Define the output Excel file path (replace ".df" with ".xlsx")
                excel_file_path = os.path.join(output_folder, os.path.splitext(file)[0] + '.xlsx')
                
                # Convert the DataFrame to Excel and save it
                dataframe_to_excel(df, excel_file_path)
                print(f'Converted {file_path} to {excel_file_path}')