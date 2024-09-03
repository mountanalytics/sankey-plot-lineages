import os
import pandas as pd
import ast
import numpy as np



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

    # Iterate over rows of the DataFrame
    for index, row in df_labels.iterrows():
        if 'DataSources' in row['FUNCTION']:
            # Extract only the desired columns and rename 'FILTER' to 'COUNT'
            filtered_row = row[['LABEL_NODE', 'ID', 'FILTER']].rename({'FILTER': 'COUNT'})
            # Append the filtered row to the empty DataFrame
            sources = pd.concat([sources, filtered_row.to_frame().transpose()], ignore_index=True)

            
    sources['COUNT'] = 0

    info_calc = {}

    for files in list_files:
        # open lineage file
        df = pd.read_csv(f"{lineages_path}/{files}")

        # List of unique nodes
        nodes = list(set(df['TARGET_NODE']) | set(df['SOURCE_NODE']))
        
        # Filter label_nodes and function_nodes based on matching IDs
        label_nodes = df_labels[df_labels['ID'].isin(nodes)][['ID', 'LABEL_NODE']].rename(columns={'LABEL_NODE': 'LABEL_NODE'})
        function_nodes = df_labels[df_labels['ID'].isin(nodes)][['ID', 'FUNCTION']].rename(columns={'FUNCTION': 'FUNCTION'})
        
        # Count occurrences of each node in TARGET_NODE and SOURCE_NODE columns
        target_nodes = df['TARGET_NODE'].value_counts().reset_index().rename(columns={'TARGET_NODE': 'ID', 'count': 'TARGET_COUNT'})
        source_nodes = df['SOURCE_NODE'].value_counts().reset_index().rename(columns={'SOURCE_NODE': 'ID', 'count': 'SOURCE_COUNT'})
        
        # Merge label_nodes and function_nodes on 'ID'
        label_function_nodes = pd.merge(label_nodes, function_nodes, on='ID', how='outer')
        
        # Merge label_function_nodes, target_nodes, and source_nodes on 'ID'
        result = pd.merge(label_function_nodes, target_nodes, left_on='ID', right_on='ID', how='outer')
        result = pd.merge(result, source_nodes, left_on='ID', right_on='ID', how='outer')
        
        result['TARGET_COUNT'] = result['TARGET_COUNT'].fillna(0)
        result['SOURCE_COUNT'] = result['SOURCE_COUNT'].fillna(0)
        
        try:
            info_calc[files.split('-')[1].split('.')[0]] = result
        except:
            info_calc[files] = result
        """ this first part is to calcualtion how much a node is used as a source or a target node based on the columns which are fed into or arise from the node
        """ 

    filtered_data = []

    for key, df in info_calc.items():
        """ part to get the sources which source feed data into the calc view. This could also be other caluculation views"""
        filtered_df = df[df['FUNCTION'] == 'DataSources']
        if not filtered_df.empty:
            label_nodes = filtered_df['LABEL_NODE'].tolist()
            filtered_data.append({'CALC_VIEW': key, 'SOURCE': label_nodes})

    #this takes into account all the xlsx in the folder which are all the tech lineages from all the calc views

    for files in list_files:
        # open lineage file
        df = pd.read_csv(f"{lineages_path}/{files}")

        # List of unique nodes
        nodes = list(set(df['TARGET_NODE']) | set(df['SOURCE_NODE']))
        
        # Filter label_nodes and function_nodes based on matching IDs
        label_nodes = df_labels[df_labels['ID'].isin(nodes)][['ID', 'LABEL_NODE']].rename(columns={'LABEL_NODE': 'LABEL_NODE'})
        function_nodes = df_labels[df_labels['ID'].isin(nodes)][['ID', 'FUNCTION']].rename(columns={'FUNCTION': 'FUNCTION'})
        
        # Count occurrences of each node in TARGET_NODE and SOURCE_NODE columns
        target_nodes = df['TARGET_NODE'].value_counts().reset_index().rename(columns={'TARGET_NODE': 'ID', 'count': 'TARGET_COUNT'})
        source_nodes = df['SOURCE_NODE'].value_counts().reset_index().rename(columns={'SOURCE_NODE': 'ID', 'count': 'SOURCE_COUNT'})
        
        # Merge label_nodes and function_nodes on 'ID'
        label_function_nodes = pd.merge(label_nodes, function_nodes, on='ID', how='outer')
        
        # Merge label_function_nodes, target_nodes, and source_nodes on 'ID'
        result = pd.merge(label_function_nodes, target_nodes, left_on='ID', right_on='ID', how='outer')
        result = pd.merge(result, source_nodes, left_on='ID', right_on='ID', how='outer')
        
        result['TARGET_COUNT'] = result['TARGET_COUNT'].fillna(0)
        result['SOURCE_COUNT'] = result['SOURCE_COUNT'].fillna(0)
        
        try:
            info_calc[files.split('-')[1].split('.')[0]] = result
        except:
            info_calc[files] = result
        """ this first part is to calcualtion how much a node is used as a source or a target node based on the columns which are fed into or arise from the node
        """ 

    filtered_data = []

    for key, df in info_calc.items():
        """ part to get the sources which source feed data into the calc view. This could also be other caluculation views"""
        filtered_df = df[df['FUNCTION'] == 'DataSources']
        if not filtered_df.empty:
            label_nodes = filtered_df['LABEL_NODE'].tolist()
            filtered_data.append({'CALC_VIEW': key, 'SOURCE': label_nodes})

    # Make the csv files which are used for the sankey where sources are coupled to the calc views

    # Create a new dataframe from the filtered data
    result_df = pd.DataFrame(filtered_data)
    result_df = result_df.explode('SOURCE').reset_index(drop=True)

    nodes_source = list(np.unique(result_df['CALC_VIEW']))
    nodes_source.extend(np.unique(result_df['SOURCE']))
    nodes_source = pd.DataFrame(nodes_source, columns=['Name'])


    colors = []

    # add different colors to nodes depending whether they are tables or they are views
    for row in nodes_source['Name']:
        calc_views = list(result_df['CALC_VIEW'])
        if row in calc_views:
            print(row)

            colors.append('lightblue')
        else:
            colors.append('black')

    nodes_source['COLOR'] = colors
        

    result_df['CALC_ID'],result_df['SOURCE_ID'],result_df['LINK_VALUE'] = 0,0,1

    for i in range(len(result_df)):
        for j in range(len(nodes_source)):
            if result_df.at[i, 'CALC_VIEW'] == nodes_source.at[j, 'Name']:
                result_df.at[i, 'CALC_ID'] = j
            elif result_df.at[i, 'SOURCE'] == nodes_source.at[j, 'Name']:
                result_df.at[i, 'SOURCE_ID'] = j



    #result_df.to_csv("sample-data/output-tables-sql/analysis/lineage_calc_source.csv", index = False)
    #nodes_source.to_csv("sample-data/output-tables-sql/analysis/nodes_calc_source.csv", index = True)


    return result_df, nodes_source


if __name__ == '__main__':
    stack_data('sample-data/output-tables-sql/lineages', 'sample-data/output-tables-sql/nodes.csv')

 