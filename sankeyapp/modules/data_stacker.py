import os
import pandas as pd
import ast
import numpy as np


def source_target_tables(lineages: pd.DataFrame, nodes: pd.DataFrame) -> pd.DataFrame:
    unique_combinations = lineages[['SOURCE_NODE', 'TARGET_NODE']].drop_duplicates()
    
    # Merge to get SOURCE_FUNC
    unique_combinations = unique_combinations.merge(
        nodes[['ID', 'FUNCTION', "LABEL_NODE"]], 
        how='left', 
        left_on='SOURCE_NODE', 
        right_on='ID'
    ).rename(columns={'FUNCTION': 'SOURCE_FUNC', "LABEL_NODE" : "SOURCE_NAME"}).drop(columns='ID')
    
    # Merge to get TARGET_FUNC
    unique_combinations = unique_combinations.merge(
        nodes[['ID', 'FUNCTION', "LABEL_NODE"]], 
        how='left', 
        left_on='TARGET_NODE', 
        right_on='ID'
    ).rename(columns={'FUNCTION': 'TARGET_FUNC',"LABEL_NODE" : "TARGET_NAME"}).drop(columns='ID')
    
    source_tables = unique_combinations[(unique_combinations["SOURCE_FUNC"] == "DataSources") | (unique_combinations["SOURCE_FUNC"] == "DataDestinations")][['SOURCE_NODE',"SOURCE_NAME"]]
    target_tables = unique_combinations[(unique_combinations["TARGET_FUNC"] == "DataDestinations") | (unique_combinations["TARGET_FUNC"] == "DataSources")][['TARGET_NODE',"TARGET_NAME"]]
    source_tables['SourceType'] = 'source'
    target_tables['SourceType'] = 'target'

    # Rename the columns to have consistent names for merging
    source_tables = source_tables.rename(columns={"SOURCE_NODE": "Node", "SOURCE_NAME": "Name"})
    target_tables = target_tables.rename(columns={"TARGET_NODE": "Node", "TARGET_NAME": "Name"})

    # Combine the two tables
    combined_tables = pd.concat([source_tables, target_tables], ignore_index=True)
    return combined_tables



def stack_data(lineages_path, nodes_path):

    # opened stacked node and lineages data
    list_files = os.listdir(lineages_path)

    try:
        list_files.remove('lineage-merged.csv')
    except:
        pass

    df_labels = pd.read_csv(nodes_path, sep = ',')
    df_labels = df_labels.dropna(subset=['FUNCTION'])


    # get source tables
    sources = pd.DataFrame()
    targets = pd.DataFrame()
    # Iterate over rows of the DataFrame
    for index, row in df_labels.iterrows():
        if 'DataSources' in row['FUNCTION']:
            # Extract only the desired columns and rename 'FILTER' to 'COUNT'
            filtered_row = row[['LABEL_NODE', 'ID', 'FILTER']].rename({'FILTER': 'COUNT'})
            # Append the filtered row to the empty DataFrame
            sources = pd.concat([sources, filtered_row.to_frame().transpose()], ignore_index=True)
        elif 'DataDestinations' in row['FUNCTION']:
            # Extract only the desired columns and rename 'FILTER' to 'COUNT'
            filtered_row = row[['LABEL_NODE', 'ID', 'FILTER']].rename({'FILTER': 'COUNT'})
            # Append the filtered row to the empty DataFrame
            targets = pd.concat([targets, filtered_row.to_frame().transpose()], ignore_index=True)

    sources['COUNT'] = 0

    result_df = pd.DataFrame()
    
    for files in list_files:
        # open lineage file
        df = pd.read_csv(f"{lineages_path}/{files}")
        source_target = source_target_tables(df, df_labels)
        source_target["Calc_view"] = files.split(".")[0].split("-")[1]
        result_df = pd.concat([result_df,source_target],ignore_index=True)


    nodes_source = list(np.unique(result_df['Calc_view']))
    nodes_source.extend(np.unique(result_df['Name']))
    nodes_source = pd.DataFrame(nodes_source, columns=['Name'])
    
    colors = []

    # add different colors to nodes depending whether they are tables or they are views
    for row in nodes_source['Name']:
        calc_views = list(result_df['Calc_view'])
        if row in calc_views:
            print(row)

            colors.append('lightblue')
        else:
            colors.append('black')

    nodes_source['COLOR'] = colors
    nodes_source['CALC_ID'] = nodes_source.index    
    result_df['Source'] = result_df.apply(lambda row: row['Name'] if row['SourceType'] == 'source' else row['Calc_view'], axis=1)
    result_df['Target'] = result_df.apply(lambda row: row['Calc_view'] if row['SourceType'] == 'source' else row['Name'], axis=1)

    # View the updated DataFrame
    res_df = result_df[['Node', 'Source', 'Target', 'SourceType']]
    res_df['SOURCE_ID'],res_df['TARGET_ID'],res_df['LINK_VALUE'] = 0,0,1

    for i in range(len(result_df)):
        for j in range(len(nodes_source)):
            if res_df.at[i, 'Source'] == nodes_source.at[j, 'Name']:
                res_df.at[i, 'SOURCE_ID'] = j
            elif res_df.at[i, 'Target'] == nodes_source.at[j, 'Name']:
                res_df.at[i, 'TARGET_ID'] = j

    #result_df.to_csv("sample-data/output-tables-sql/analysis/lineage_calc_source.csv", index = False)
    #nodes_source.to_csv("sample-data/output-tables-sql/analysis/nodes_calc_source.csv", index = True)
    return res_df, nodes_source


if __name__ == '__main__':
    stack_data('../sample-data/output-tables-ssis/lineages', '../sample-data/output-tables-ssis/nodes.csv')

 