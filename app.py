from flask import Flask, render_template, request, g
import plotly.graph_objs as go
from modules.sankey import sankey_plot
from modules.sankey import sankey_stacked
import plotly
import json
import pandas as pd
import os

app = Flask(__name__)




def get_files(path):
    """
    Function that returns a list of files available as option on the Flask frontend
    """
    list_files = os.listdir(path)
    # Initialize empty lists to store extracted substrings
    options = []
    
    # Iterate over each file name
    for file_name in list_files:
        # Split the file name by '-' and get the second part (after the '-')
        extracted_string = file_name.split('-')[1]
        # Remove the file extension (.csv) by splitting again and taking the first part
        extracted_string = extracted_string.split('.')[0]
       

        # Append the extracted substring to the list
        options.append(extracted_string)
        try:
            options.remove('merged')
        except:
            pass
    return options




@app.route('/', methods=['GET', 'POST'])
def index():

    lineages_path = app.config.get('LINEAGES_PATH', 'output-tables-ssis/lineages/')
    nodes_path = app.config.get('NODES_PATH', 'output-tables-ssis/nodes.csv')

    options = get_files(lineages_path)
    
    if request.method == 'GET':
        a = sankey_plot.draw_sankey([options[0]], lineages_path, nodes_path)
        plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)
        
    if request.method == 'POST':
        selected_options = request.form.getlist('option')
        stacked_overview_checked = 'stackedOverview' in request.form
        if stacked_overview_checked:
            a = sankey_stacked.sankey_stacked("output-tables-sql/analysis/lineage_calc_source.csv", 'output-tables-sql/analysis/nodes_calc_source.csv')
            plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)
        else:
            print(selected_options)
            print(lineages_path)
            a = sankey_plot.draw_sankey(selected_options, lineages_path, nodes_path)
            plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)
    form_width = 270

    return render_template('index.html', options=options, graphJSON=plot_json, form_width=form_width)


if __name__ == '__main__':

    app.config['LINEAGES_PATH'] = 'output-tables-sql/lineages/'
    app.config['NODES_PATH'] = 'output-tables-sql/nodes.csv'    
    app.run(debug=True)
