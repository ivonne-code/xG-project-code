import pandas as pd

def load_and_adjust_csv(file_path):
    # Load the existing CSV file
    df = pd.read_csv('argentina_player_stats_pt.csv')
    
    # Display the first few rows to understand what corrections are needed
    print("Original Data:")
    print(df.head())
    
    # Define the exact headers as they should appear based on your screenshot
    correct_headers = [
        'Player', '#', 'Pos', 'Age', 'Min', 'Att', 'Live', 'Dead', 'FK', 'TB', 'Sw', 'Crs', 'TI', 'CK', 'In', 'Out', 'Str', 'Cmp', 'Off', 'Blocks'
    ]
    
    # Check if all correct headers are in the DataFrame, otherwise add them as empty columns
    for header in correct_headers:
        if header not in df.columns:
            df[header] = ''

    # Rearrange columns to match the exact order you need
    df = df[correct_headers]
    
    # Save the adjusted DataFrame back to CSV
    df.to_csv('adjusted_argentina_player_stats_pt.csv', index=False)
    print("Adjusted Data:")
    print(df.head())

# Assuming the path to your CSV file
csv_file_path = 'argentina_player_stats_pt.csv'
load_and_adjust_csv(csv_file_path)
