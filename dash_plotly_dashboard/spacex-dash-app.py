# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
from pathlib import Path

# Read the airline data into pandas dataframe
spacex_path = Path(__file__).parent / "spacex_launch_dash.csv"
spacex_df = pd.read_csv(spacex_path)
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"},
                *[
                    {"label": site, "value": site}
                    for site in spacex_df["Launch Site"].unique()
                ],
            ],
            value="ALL",
            placeholder="Filter by launch site",
            searchable=True,
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10_000,
            step=1_000,
            marks={
                tick: str(tick)
                for tick in range(0, 10_000 + 1, 500)  # Every 500
            },
            value=[
                4_000,
                6_000,
            ],
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def update_pie_graph_on_site_selection(selection_value):
    if selection_value == "ALL":
        data = spacex_df.groupby("Launch Site")["class"].mean().reset_index()  # pyright: ignore[reportAttributeAccessIssue]
        fig = px.pie(data, values="class", names="Launch Site")
    else:
        fig = px.pie(
            spacex_df[spacex_df["Launch Site"] == selection_value]["class"]
            .value_counts()  # pyright: ignore[reportAttributeAccessIssue]
            .reset_index(),
            values="count",
            names="class",
            title=f"Success rate of launch from {selection_value}",
        )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def update_scatterplot_on_site_selection(site_selection_value, payload_mass_range):
    # Filter by mass
    min_, max_ = payload_mass_range
    data = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= min_)
        & (spacex_df["Payload Mass (kg)"] <= max_)
    ]

    # Filter by site(if needed)
    if site_selection_value != "ALL":
        data = data[data["Launch Site"] == site_selection_value]

    # Task is stated identically for both If-Else branches
    fig = px.scatter(
        data, x="Payload Mass (kg)", y="class", color="Booster Version Category"
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run()
