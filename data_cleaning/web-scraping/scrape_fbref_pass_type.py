import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def find_player_stats_table(soup, team_name):
    all_tables = soup.find_all('table')
    for table in all_tables:
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'Player' in headers and 'Min' in headers and team_name in table.get_text():
            return table
    return None  # Return None if no table matches
# URL of the match page
url = 'https://fbref.com/en/matches/7140acae/Argentina-France-December-18-2022-World-Cup'
soup = fetch_and_parse(url)

# Extract tables for both teams
argentina_stats_table = find_player_stats_table(soup, "Argentina")
france_stats_table = find_player_stats_table(soup, "France")

# Function to parse the table data
def parse_table(table):
    rows = table.find_all('tr')
    table_data = []
    for row in rows:
        cells = row.find_all(['th', 'td'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        # Adjust row length if necessary (example: merge some columns)
        if len(row_data) > 21:  # Suppose we expect no more than 31 columns
            row_data = row_data[:21]  # Adjust this based on your specific needs
        table_data.append(row_data)
    return table_data

# Assuming you have a function called parse_table that extracts table data
argentina_data = parse_table(argentina_stats_table) if argentina_stats_table else []
france_data = parse_table(france_stats_table) if france_stats_table else []


# Manually specify the full list of headers based on the expected table structure
full_headers = ['Player', '#', 'Pos', 'Age', 'Club', 'Min', 'Att', 'Live', 'Dead', 'FK', 'TB', 'Sw', 'Crs', 'TI', 
                'CK', 'In', 'Out', 'Str', 'Cmp', 'Off', 'Blocks']

def save_to_csv(data, filename):
    if not data or len(data) < 2:
        print(f"No valid data found for {filename}.")
        return
    
    # Create DataFrame assuming the first row of data is not needed for headers
    df = pd.DataFrame(data[1:], columns=full_headers)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Assuming data extraction is done correctly and 'argentina_data' and 'france_data' are available
save_to_csv(argentina_data, 'argentina_player_stats_pt.csv')
save_to_csv(france_data, 'france_player_stats_pt.csv')
