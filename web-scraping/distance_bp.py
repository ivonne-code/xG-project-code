import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def find_shots_table(soup):
    """Find the specific shots table by checking header content."""
    all_tables = soup.find_all('table')
    for table in all_tables:
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        # Ensure these headers match the specifics of the shots table
        if 'Minute' in headers and 'Player' in headers and 'Squad' in headers and 'xG' in headers:
            return table
    return None  # Return None if no table matches


# Function to parse the table data
def parse_table(table):
    rows = table.find_all('tr')
    table_data = []
    for row in rows:
        cells = row.find_all(['th', 'td'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        # Adjust row length if necessary (example: merge some columns)
        if len(row_data) > 13:  # Suppose we expect no more than 31 columns
            row_data = row_data[:13]  # Adjust this based on your specific needs
        table_data.append(row_data)
    return table_data

# Manually specify the full list of headers based on the expected table structure
full_headers = ['Minute','Player','Squad','xG','PSxG','Outcome','Distance','Body Part','Notes','Player','Event','Player','Event']

def save_to_csv(data, filename):
    if not data or len(data) < 2:
        print(f"No valid data found for {filename}.")
        return
    
    # Create DataFrame assuming the first row of data is not needed for headers
    df = pd.DataFrame(data[1:], columns=full_headers)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    url = 'https://fbref.com/en/matches/7140acae/Argentina-France-December-18-2022-World-Cup'
    soup = fetch_and_parse(url)
    
    # Make sure only one argument is passed here
    shots_table = find_shots_table(soup)
    if shots_table:
        shot_data = parse_table(shots_table)
        save_to_csv(shot_data, 'shot_data.csv')
    else:
        print("No shots table found.")

if __name__ == "__main__":
    main()


