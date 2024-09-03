from flask import Flask, render_template, request
import plotly.graph_objs as go
from modules.sankey import sankey_plot
from modules.sankey import sankey_stacked
import plotly
import json
import os

app = Flask(__name__)

class SankeyApp:
    def __init__(self, lineages_path, nodes_path):
        self.lineages_path = lineages_path
        self.nodes_path = nodes_path

    def get_files(self):
        """
        Function that returns a list of files available as options on the Flask frontend
        """
        list_files = os.listdir(self.lineages_path)
        options = []

        # Iterate over each file name and extract the string as needed
        for file_name in list_files:
            if '-' in file_name:
                extracted_string = file_name.split('-')[1].split('.')[0]
                options.append(extracted_string)
            else:
                extracted_string = file_name#.split('-')[1].split('.')[0]
                options.append(extracted_string)

        # Remove 'merged' from options if it exists
        if 'merged' in options:
            options.remove('merged')

        return options

    def create_routes(self):
        """
        Defines the routes using Flask's app decorator
        """

        @app.route('/', methods=['GET', 'POST'])
        def index():
            options = self.get_files()  # Get the file options
            print(options)

            if request.method == 'GET':
                # On GET, render a default Sankey plot
                a = sankey_plot.draw_sankey([options[0]], self.lineages_path, self.nodes_path)
                plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)

            if request.method == 'POST':
                # Handle form submission
                selected_options = request.form.getlist('option')
                stacked_overview_checked = 'stackedOverview' in request.form

                if stacked_overview_checked:
                    # If stacked overview is checked, render stacked Sankey plot
                    a = sankey_stacked.sankey_stacked("output-tables-sql/analysis/lineage_calc_source.csv", 'output-tables-sql/analysis/nodes_calc_source.csv')
                    plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)
                else:
                    # Otherwise, render the selected Sankey plot
                    a = sankey_plot.draw_sankey(selected_options, self.lineages_path, self.nodes_path)
                    plot_json = json.dumps(a, cls=plotly.utils.PlotlyJSONEncoder)

            form_width = 270
            return render_template('index.html', options=options, graphJSON=plot_json, form_width=form_width)


if __name__ == '__main__':
    # Create the SankeyApp instance
    sankey_app = SankeyApp('sample-data/output-tables-sap/lineages/', 'sample-data/output-tables-sap/nodes.csv')
    
    # Register the routes
    sankey_app.create_routes()
    
    # Run the Flask app
    app.run(debug=True)
