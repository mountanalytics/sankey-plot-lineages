from . import app
from .routes import SankeyApp

def main(lineages_path, nodes_path, merge_node, error_path):
    # Initialize the SankeyApp
    sankey_app = SankeyApp(lineages_path, nodes_path,merge_node, error_path)
    sankey_app.create_routes()

    # Run the Flask app
    app.run(debug=True)


if __name__ == '__main__':
    main('./sample-data/output-tables-ssis/lineages/', './sample-data/output-tables-ssis/nodes.csv')