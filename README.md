# SankeyApp

**SankeyApp** is a Python application for visualizing Sankey diagrams of data flows using Flask and Plotly. This application allows users to interactively explore data flow and relationships through Sankey diagrams, either on the file level or table-column level.

## Features

- Interactive Sankey diagrams using Plotly.
- Flask-based web interface for easy user interaction.
- Ability to handle different data sources for flexible visualization.

## Installation

### Prerequisites

- Python 3.11 or later
- Pip (Python package installer)
- A virtual environment is recommended

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/mountanalytics/sankey-plot-lineages.git
    cd sankey-plot-lineages
    ```

2. **Create and activate a virtual environment:**

    ```bash
    conda create -n env python==3.11
    conda activate env
    ```

3. **Install the required packages:**

    ```bash
    pip install -e .
    ```

## Usage

1. **Run the application:**

    ```bash
    python sankeyapp.app
    ```

    This command starts the Flask development server and makes the application accessible at `http://127.0.0.1:5000/` by default.

    To run the application from a Python file:

   
    ```python
    from sankeyapp.app import main 
    
    main(lineages_path, nodes_path) # e.g.: main('output-data/lineages/', 'output-data/nodes.csv') 
    ```

3. **Access the web interface:**

    Open your web browser and navigate to `http://127.0.0.1:5000/` to interact with the application.

4. **Interact with Sankey diagrams:**

    - Use the menu to select different data sources for the Sankey diagrams.
    - Use checkboxes to toggle different visualization options (e.g., stacked view).
  
## Configuration

### Data Files

#### Lineages Data

The lineages data path should reference a folder with lineage CSV datasets (one for each of the files), they contain all the information regarding the lineages of the Sankey grap. 
These datasets represent the flow on the column-level.
The CSV files are named **lineage-nameoffile.csv**.
Each CSV file with the following columns:


- **`SOURCE_FIELD`**: 
  - **Description**: The column name from the source node.

- **`TARGET_FIELD`**: 
  - **Description**: The output column name, which is different from the SOURCE_COLUMNS only when the name has been changed.
 
- **`SOURCE_NODE`**: 
  - **Description**: The numeric identifier or name of the source node in the context of data visualization or flow.

- **`TARGET_NODE`**: 
  - **Description**: The numeric identifier or name of the node in the context of data visualization or flow.

- **`TRANSFORMATION`**: 
  - **Description**: A description or formula specifying how the column should be transformed or computed.

- **`ROW_ID`**: 
  - **Description**: An numeric identifier for the row within the data file, used for tracking or referencing specific rows.

- **`LINK_VALUE`**: 
  - **Description**: The value used to link or map data between source and target columns, set it to default: 1.

- **`COLOR`**: 
  - **Description**: The color associated with the data or link, should be a different color when a transformation is applied (aliceblue if no transformation else orangered).


**Example:**

| TRANSFORMATION                                               | ROW_ID | LINK_VALUE | SOURCE_NODE | TARGET_NODE | SOURCE_FIELD | TARGET_FIELD | COLOR    |
|--------------------------------------------------------------|-----------|--------|------------|-------------|-------------|--------------|--------------|
|                                                              | 0      | 1          | 8.0         | 12          | loan_id      | loan_id      | aliceblue|
|SUM(MUL(payment_amount, (DIV(DIV(interest_rate, 100), 12))))  | 0      | 1          | 8.0         | 12          | payment_amount| total_interest| orangered|
|SUM(MUL(payment_amount, (DIV(DIV(interest_rate, 100), 12))))  | 0      | 1          | 13.0        | 12          | interest_rate | total_interest| orangered|

#### Nodes Data

The nodes data path references one dataset, it contains all the information regarding the nodes of the Sankey graph. 
These datasets represent the flow on the table-level.
The nodes data contains the following columns:


- **`LABEL_NODE`**: 
  - **Description**: The name of the node within the data model.
 
- **`NAME_NODE`**: 
  - **Description**: The name of the node as it is referenced in the data model or workflow. It often corresponds to a specific data source or projection.

- **`ID`**: 
  - **Description**: A unique identifier for the node. It serves as a reference to distinguish between different nodes and it is used to merge the nodes data with the lineages data.

- **`FUNCTION`**: 
  - **Description**: The role or type of the node, describing the functionality or process that the node represents (e.g., DataSources, ProjectionView, Subquery, Variable, JoinView...), Source tables should always be DataSources and destination tables DataDestinations.
  - 
- **`JOIN_ARG`** (optional): 
  - **Description**: The argument or field used to join two or more tables.
 
- **`SPLIT_ARG`** (optional): 
  - **Description**: The argument or field used to split a table.
 
- **`ON`** (optional): 
  - **Description**: The field used to join two tables in SQL.

- **`FILTER`**: 
  - **Description**: The filter condition applied to the data, typically expressed in SQL-like syntax. This field specifies the criteria that must be met for the data to be included.

- **`COLOR`**: 
  - **Description**: The color associated with the node, should be a different color in case there is a FILTER, a JOIN_ARG/SPLIT_ARG/ON and depending on the function of the node..

**Example:**


| LABEL_NODE               | ID  | FUNCTION        | JOIN_ARG | NAME_NODE        | FILTER | COLOR |
|--------------------------|-----|-----------------|----------|------------------|--------|-------|
| BILLING_DOC_HDR           | 0   | DataSources     |          | BILLING_DOC_HDR  |        | black |
| B_BillingHdr@BillingDocHdr_P | 1   | ProjectionView  |          | BillingDocHdr_P  |        | black |
| B_BillingHdr@Semantics    | 2   | Semantics       |          | Semantics        |        | black |





