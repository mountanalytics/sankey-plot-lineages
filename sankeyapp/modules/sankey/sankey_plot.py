from flask import Flask, render_template, request
import plotly.graph_objs as go
import pandas as pd

def delete_error_inp(package: str, path: str, node_path: str, order_node: str, error_path: str):
    df_lin = pd.read_csv(f"{path}lineage-{package}.csv")
    nodes = pd.read_csv(f"{node_path}")
    df_order = pd.read_csv(f"{order_node}order_nodes-{package}.csv")
    markers = pd.read_csv(f"{order_node}marker_nodes-{package}.csv")
    
    id_block_out_list = list(df_order["ID_block_out"])
    
    for marker in markers["NAME"]:
        ref = marker
        marked_nodes = []
        marked_nodes.append(ref.split("\\")[1] + "@" + ref.split("\\")[2])
        while ref in id_block_out_list:
            idx = id_block_out_list.index(ref)  # Find the index of 'ref'
            ref = df_order.at[idx, "ID_block_in"]
            ref.split()
            marked_nodes.append(ref.split("\\")[1] + "@" + ref.split("\\")[2])
    
    nodes["MARKER"] = 0
    nodes["MARKER"] = nodes["LABEL_NODE"].isin(marked_nodes).astype(int)
   
    nodes_del = list(nodes[nodes["MARKER"] == 1]["ID"])
    df_lin = df_lin[~df_lin["SOURCE_NODE"].isin(nodes_del) & ~df_lin["TARGET_NODE"].isin(nodes_del)]
    df_lin.to_csv(f"{error_path}del-error-{package}.csv")
    return

def hard_coded(node_path: str):
    nodes = pd.read_csv(f"{node_path}")
    block = list(nodes["NAME_NODE"])
    for index, row in nodes.iterrows():
        # Convert SPLIT_ARG and FILTER to strings to handle NaNs safely
        split_arg_str = str(row["SPLIT_ARG"])
        filter_str = str(row["FILTER"])
        
        # Check conditions
        if (any(name in split_arg_str for name in block) or any(name in filter_str for name in block)) \
        or (pd.isna(row["SPLIT_ARG"]) and pd.isna(row["FILTER"])):
            nodes.at[index, "COLOR"] = "black"
        elif pd.notna(row["SPLIT_ARG"]) or pd.notna(row["FILTER"]):
            nodes.at[index, "COLOR"] = "red"
    return nodes["COLOR"]

def draw_sankey(name:str, lineages_path:str, nodes_path:str, error_path: str, marks: str):
    """
    Dashboard logic
    """
    if marks == "normal" or marks == "hard_code":
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
    elif marks == "del":
        df = pd.read_csv(f'{error_path}/del-error-{name[0]}.csv')
        title = f"Sankey of control node: {name[0]}"

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
    if marks == "hard_code":
        df_labels["COLOR"] = hard_coded(nodes_path)
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