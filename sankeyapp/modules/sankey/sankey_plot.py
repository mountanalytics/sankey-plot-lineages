from flask import Flask, render_template, request
import plotly.graph_objs as go
import pandas as pd

def draw_sankey(name:str, lineages_path:str, nodes_path:str):
    """
    Dashboard logic
    """
    if len(name) == 1: # if only one view
        df = pd.read_csv(f'{lineages_path}/lineage-{name[0]}.csv')
        title = f"Sankey of control node: {name[0]}"
    else:
        lineage_list = []
        if len(name) == 2: # if 2 views
            title = f"Sankey of merged control nodes: {name[0]} and {name[1]}"
        else: # if more than 2
            title = "Sankey of multiple merged control nodes"


        for lins in name: 
            lineage = pd.read_csv(f"{lineages_path}/lineage-{lins}.csv")
            lineage_list.append(lineage)

        df = pd.concat(lineage_list, ignore_index=True)


    df_labels = pd.read_csv(nodes_path, sep = ',')

    df['source_to_target'] = df[['SOURCE_FIELD', 'TARGET_FIELD']].agg('=>'.join, axis=1)

    df['source_to_target_transformation'] = df[['source_to_target', 'TRANSFORMATION']].apply(
        lambda x: '{}<br />Transformation: {}'.format(x[0], x[1]) if pd.notna(x[1]) else x[0],
        axis=1
    )


    transformation_columns = ['FILTER', 'JOIN_ARG', 'SPLIT_ARG', 'WHERE_ARG', 'ON_ARG']
    for col in transformation_columns:
        if col not in df_labels.columns:
            df_labels[col] = pd.NA

    df_labels['hover_label'] = df_labels[['LABEL_NODE', 'FILTER', 'JOIN_ARG', 'SPLIT_ARG', 'WHERE_ARG', 'ON_ARG']].apply(
        lambda x: '{}{}'.format(
            x[0],
            f'<br />Filter: {x[1]}' if pd.notna(x[1]) else '') 
        + (f'<br />Join Argument: {x[2]}' if pd.notna(x[2]) else '') 
        + (f'<br />Split Argument: {x[3]}' if pd.notna(x[3]) else '')
        + (f'<br />Where Argument: {x[4]}' if pd.notna(x[4]) else '')
        + (f'<br />On Argument: {x[5]}' if pd.notna(x[5]) else '')
        ,
        axis=1
    )

    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 20,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = df_labels['LABEL_NODE'],
            customdata = df_labels['hover_label'],
            hovertemplate='%{customdata}',
            color = df_labels['COLOR']
        ),
        link = dict(
        #arrowlen=15,
        line = dict(color = "blue", width = 0.05),
        hoverlabel = dict (font = dict(size=15) ),
        source = df['SOURCE_NODE'], # indices correspond to labels, eg A1, A2, A2, B1, ...
        target = df['TARGET_NODE'],
        value = df['LINK_VALUE'],
        customdata = df['source_to_target_transformation'],
        hovertemplate='Details: %{customdata}',
        color = df['COLOR'],
    ),
    
        
    )])
    fig.update_layout(font_size=10)
    fig.update_layout(title = dict(text=title, font_size=20))
    return fig