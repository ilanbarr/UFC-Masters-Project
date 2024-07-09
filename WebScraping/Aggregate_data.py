import pandas as pd

urls_df = pd.read_csv('all_links.csv') 
urls = urls_df['URL'].tolist() 
urls

dfs = []

for url in urls:
    try:
        df = scrape_data(url)
        dfs.append(df)
    except Exception as e:
        print(f"Failed to scrape {url} due to {e}")

final_df = pd.concat(dfs, ignore_index=True)

final_df.to_pickle('final_data.pkl')