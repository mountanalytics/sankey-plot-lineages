import pandas as pd
import plotly.graph_objects as go

#def sankey_stacked(lineages_path:str, nodes_path:str):
    
#    df = pd.read_csv(lineages_path)
#    df_labels = pd.read_csv(nodes_path)

def sankey_stacked(stacked_lineages:pd.DataFrame, stacked_nodes:pd.DataFrame):
    
    df = stacked_lineages.copy()
    df_labels = stacked_nodes.copy()

    df = df.rename(columns = {"CALC_VIEW" : "TARGET_FIELD", 'SOURCE' : 'SOURCE_FIELD', "CALC_ID" : "TARGET_NODE", "SOURCE_ID" : "SOURCE_NODE"})
    df_labels = df_labels.rename(columns = {"Unnamed: 0" : "LABEL_NODE"})
    
    df['source_to_target'] = df[['SOURCE_FIELD', 'TARGET_FIELD']].agg('=>'.join, axis=1)
    
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 20,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = df_labels['Name'],
          color = df_labels['COLOR'],
         
          #hovertemplate='Node %{customdata} has total value %{value}<extra></extra>',
          #scolor = "lightblue"
    
        ),
        link = dict(
          #arrowlen=15,
          line = dict(color = "blue", width = 0.05),
          hoverlabel = dict (font = dict(size=15) ),
          source = df['SOURCE_NODE'], 
          target = df['TARGET_NODE'],
          value = df['LINK_VALUE'],
          customdata = df['source_to_target'],
          hovertemplate='Details: %{customdata}',
          color = 'lightgrey', #df['COLOR'],
    
          #hovertemplate='Link from node %{source.customdata}<br />'+'to node%{target.customdata}<br />has value %{value}'+ '<br />and data %{customdata}<extra></extra>',
      ),
      )])
    
    fig.update_layout(font_size=10)
    fig.update_layout(title = dict(text="Data sources coupled to the calculation views", font_size=20))
    return fig