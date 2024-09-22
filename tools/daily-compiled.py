import os
import pandas as pd
import re
from datetime import datetime

def process_csv(file_path):
    df = pd.read_csv(file_path)
    grouped = df.groupby(['country', 'origin', 'system', 'status']).size().reset_index(name='count')
    pivoted = grouped.pivot_table(values='count', index=['country', 'origin', 'system'], 
                                  columns='status', fill_value=0).reset_index()
    
    pivoted = pivoted.rename(columns={
        'destroyed': 'destroyed',
        'abandoned': 'abandoned',
        'captured': 'captured',
        'damaged': 'damaged'
    })
    
    pivoted['type_total'] = pivoted['destroyed'] + pivoted['abandoned'] + pivoted['captured'] + pivoted['damaged']
    
    pivoted = pivoted.rename(columns={'system': 'equipment_type'})
    
    return pivoted

def create_daily_totals(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_totals = []
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_dir, filename)
            
            daily_totals = process_csv(input_path)
            
            all_types = daily_totals.groupby('country').sum().reset_index()
            all_types['equipment_type'] = 'All Types'
            all_types['origin'] = ''
            
            daily_totals = pd.concat([all_types, daily_totals], ignore_index=True)
            
            date_str = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            if date_str:
                date = datetime.strptime(date_str.group(1), '%Y-%m-%d').date()
            else:
                date = None
            
            daily_totals['date'] = date
            
            all_totals.append(daily_totals)
    
    combined_totals = pd.concat(all_totals, ignore_index=True)
    
    column_order = ['date', 'country', 'origin', 'equipment_type', 'destroyed', 'abandoned', 'captured', 'damaged', 'type_total']
    combined_totals = combined_totals[column_order]
    
    output_path = os.path.join(output_dir, 'combined_totals.csv')
    combined_totals.to_csv(output_path, index=False)
    print(f"Processed all files and saved combined totals to {output_path}")
    

if __name__ == "__main__":
    input_directory = 'outputfiles/daily'
    output_directory = 'outputfiles/'
    create_daily_totals(input_directory, output_directory)