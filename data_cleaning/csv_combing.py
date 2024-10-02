import pandas as pd

file_path_pt = '/Users/yifengluo/Downloads/xG-project-code-main/xG-project-code/data_cleaning/web-scraping/Argentina_France_pt.csv'
df_pt = pd.read_csv(file_path_pt)
file_path_st = '/Users/yifengluo/Downloads/xG-project-code-main/xG-project-code/data_cleaning/web-scraping/shots_ap.csv'
df_st = pd.read_csv(file_path_st)
combined_df = pd.concat([df_pt, df_st], ignore_index=True)
combined_df = combined_df.iloc[1:]

combined_df = combined_df.dropna()