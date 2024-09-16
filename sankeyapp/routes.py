from flask import render_template, request
import json
import plotly
from . import app
from .modules.sankey import sankey_plot, sankey_stacked
from .modules import data_stacker
import os


class SankeyApp:
    def __init__(self, lineages_path, nodes_path, merge_node, error_path):
        self.lineages_path = lineages_path
        self.nodes_path = nodes_path
        self.merge_node = merge_node
        self.error_path = error_path

    def get_files(self):
        """
        Method to get all the lineages files and convert them to option for the flask app's menu
        """
        list_files = os.listdir(self.lineages_path)
        options = [file_name.split('-')[1].split('.')[0] for file_name in list_files if '-' in file_name]
        if 'merged' in options:
            options.remove('merged')
        return options

    def create_routes(self):
        @app.route('/', methods=['GET', 'POST'])
        def index():
            options = self.get_files()

            if request.method == 'GET':
                a = sankey_plot.draw_sankey([options[0]], self.lineages_path, self.nodes_path,self.error_path,"normal")
                plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)

            if request.method == 'POST':
                selected_options = request.form.getlist('option')
                print(selected_options)
                stacked_overview_checked = 'stackedOverview' in request.form
                mainline = 'Mainline' in request.form
                if stacked_overview_checked:
                    
                    # get the stacked dataframes
                    stacked_lineages, stacked_nodes = data_stacker.stack_data(self.lineages_path, self.nodes_path)
                    # visualize stacked
                    a = sankey_stacked.sankey_stacked(stacked_lineages, stacked_nodes)
                    
                    #a = sankey_stacked.sankey_stacked("output-tables-sql/analysis/lineage_calc_source.csv", 'output-tables-sql/analysis/nodes_calc_source.csv')
                    plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)
                elif mainline:
                    sankey_plot.delete_error_inp(selected_options[0], self.lineages_path, self.nodes_path, self.merge_node, self.error_path) 
                    a = sankey_plot.draw_sankey(selected_options, self.error_path, self.nodes_path,self.error_path,"del")
                    plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    a = sankey_plot.draw_sankey(selected_options, self.lineages_path, self.nodes_path,self.error_path,"normal")
                    plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)

            form_width = 270
            return render_template('index.html', options=options, graphJSON=plot_json, form_width=form_width)
