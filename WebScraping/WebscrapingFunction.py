import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_data_from_link(url):
    
    response = requests.get(url)
    html_content = response.text
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sections = soup.find_all('section', class_='b-fight-details__section js-fight-section')
    for section in sections:
        if section.find('table', class_='b-fight-details__table js-fight-table'):
            fight_section = section
            break
    else:
        fight_section = None

    if fight_section:
        print("Fight section with table found.")

    else:
        print("Fight section with the desired table not found.")
        
    table = fight_section.find('table', class_='b-fight-details__table js-fight-table')
    
    headers = []
    if table:
        header_row = table.find('thead').find_all('th')
        headers = [header.get_text(strip=True) for header in header_row]
        headers.insert(0, 'Round')
        # print("Headers:", headers)
    else:
        print("Table not found within the section.")
        
        
    if table:
        all_rows_data = []
        current_round = '' 

  
        for tbody in table.find_all('tbody'):
            rows = tbody.find_all(['tr', 'th']) 
            for row in rows:
                # Check if the row is a round header
                if row.name == 'th':
                    # Extract the round number from the header
                    current_round = row.get_text(strip=True)
                    continue  # Skip further processing for header rows

                cells = row.find_all('td')
                # Initialize lists to hold data for two fighters in the row, including the current round
                fighter_1_data = [current_round]
                fighter_2_data = [current_round]
                for cell in cells:
                    # Extract texts from each <p> tag within the cell
                    stats = [p.get_text(strip=True) for p in cell.find_all('p')]
                    if len(stats) == 2:
                        fighter_1_data.append(stats[0])
                        fighter_2_data.append(stats[1])
                    elif len(stats) == 1:  # Handling the case where there might be only one stat in a cell
                        fighter_1_data.append(stats[0])
                        fighter_2_data.append('')  # Append an empty string if no stat for the second fighter
                    else:  # If no <p> tags or an unexpected number, append placeholders or handle accordingly
                        fighter_1_data.append('N/A')
                        fighter_2_data.append('N/A')

                # Append the processed data for both fighters to all_rows_data
                all_rows_data.append(fighter_1_data)
                all_rows_data.append(fighter_2_data)

        # Print each row's data for verification
        # for row_data in all_rows_data:
        #     print(row_data)
    else:
        print("No table found.")
        
        
    if table:
        for tbody in table.find_all('tbody'):
            rows = tbody.find_all('tr')
            for row in rows:
                # Assuming the first column contains fighter names with links
                fighter_links = row.find_all('td')[0].find_all('a')
#                 for link in fighter_links:
#                     print(f"Fighter Name: {link.text}, URL: {link['href']}")
                    
                    

    df_total_data_by_round = pd.DataFrame(all_rows_data, columns=headers)
    df_total_data_by_round['Round'] = df_total_data_by_round['Round'].str.replace('Round ', '')

    # Convert the column to numeric, if needed
    df_total_data_by_round['Round'] = pd.to_numeric(df_total_data_by_round['Round'])

    
    
    # Find the section that contains the "Significant Strikes" marker
    significant_strikes_section = soup.find('p', class_='b-fight-details__collapse-link_tot', string=lambda text: 'Significant Strikes' in text if text else False).parent

    if significant_strikes_section:
        print("Significant Strikes section found.")
        # Now, find the table within this section
        significant_strikes_table = significant_strikes_section.find_next('table', class_='b-fight-details__table js-fight-table')

        



    if significant_strikes_table:
        # Adjust headers to exclude 'Fighter'
        headers = ['Round']  # Starting with 'Round' only
        header_row = significant_strikes_table.find('thead').find_all('th')
        headers += [header.get_text(strip=True) for header in header_row]  # Append other headers

        all_rows_data = []
        current_round = 1  # Initialize round counter

        tbody_elements = significant_strikes_table.find_all('tbody')
        for tbody in tbody_elements:
            rows = tbody.find_all('tr')
            for row in rows:
                # Initialize data rows without 'Fighter' placeholder
                fighter_1_data = [current_round]  # Assume first entry is round number
                fighter_2_data = [current_round]  # Assume first entry is round number

                cells = row.find_all('td')
                for cell in cells:
                    p_tags = cell.find_all('p')
                    if len(p_tags) == 2:  # Assuming there are always 2 <p> tags for 2 fighters
                        fighter_1_data.append(p_tags[0].get_text(strip=True))
                        fighter_2_data.append(p_tags[1].get_text(strip=True))
                    elif len(p_tags) == 1:  # Handling cases with only one <p> tag
                        fighter_1_data.append(p_tags[0].get_text(strip=True))
                        fighter_2_data.append('')  # Placeholder or logic to handle missing data

                # Append each fighter's data as a separate row
                all_rows_data.append(fighter_1_data)
                all_rows_data.append(fighter_2_data)

            # Assume each tbody represents a new round; increment the round counter
                current_round += 1

        # Create DataFrame
        df_sig_strikes = pd.DataFrame(all_rows_data, columns=headers)
        # print(df_sig_strikes.head())
    # else:
    #     print("Significant Strikes table not found.")
        
        
        
    df_final_total = pd.merge(df_total_data_by_round,df_sig_strikes,left_on=['Round','Fighter','Sig. str.','Sig. str. %'], right_on=['Round','Fighter','Sig. str','Sig. str. %'])
    df_final_total['URL'] = url
    return (df_final_total)