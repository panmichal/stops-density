# Import packages
from dash import Dash, html, State, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objs as go
import json


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = [
    html.Div([
        dbc.Row(dbc.Col(html.H4('Stops density by area')), justify="center"), 
        dbc.Row(dbc.Col(html.Div(className='row', children = [
            dcc.Input(id="geometry-file", type="text", placeholder="Enter geometry (Geojson, Shapefile etc.) source"),
            dcc.Input(id="gtfs-file", type="text", placeholder="Enter GTFS source"),
            html.Button('Submit', id='submit-geometry', n_clicks=0)
        ])), justify="center"),
        dbc.Row(dbc.Col(html.Div([dcc.Graph(id="graph")])), justify="center")
        ])
]

@app.callback(
    Output("graph", "figure"), 
    Input("submit-geometry", "n_clicks"),
    State("geometry-file", "value"),
    State("gtfs-file", "value"))
def display_scatter(n_clicks, geojson_file, gtfs_dir):
    gdf = gpd.read_file(geojson_file)
    gdf = gdf.to_crs(epsg=4258)
    stops_file = gtfs_dir + '/stops.txt'
    gtfs_df = pd.read_csv(stops_file)
    gtfs_gdf = gpd.GeoDataFrame(gtfs_df, geometry=gpd.points_from_xy(gtfs_df.stop_lon, gtfs_df.stop_lat))
    # gtfs_gdf = gpd.sjoin(gtfs_gdf, gdf, how="left")
    # gtfs_gdf = gtfs_gdf.groupby('id').size().reset_index(name='count')
    # gtfs_gdf = gtfs_gdf.rename(columns={'id': 'id_area'})
    # gdf = gdf.merge(gtfs_gdf, on='id_area', how='left')
    # gdf['count'] = gdf['count'].fillna(0)
    # gdf['area'] = gdf['geometry'].area
    # gdf['stops_density'] = gdf['count'] / gdf['area']
    # fig = px.choropleth_mapbox(gdf, geojson=gdf.geometry, locations=gdf.index, color="stops_density",
    #                        hover_data=["id_area", "count", "area", "stops_density"],
    #                        mapbox_style="carto-positron",
    #                        zoom=11, center = {"lat": 51.11046075118283, "lon": 17.03258604846201},
    #                        opacity=0.5,
    #                        labels={'stops_density':'stops density'})
    # Center of Wrocław
    point = (51.11046075118283, 17.03258604846201)
    fig = go.Figure(px.scatter_mapbox(gdf, lat=[point[0]], lon=[point[1]]).update_layout(
        mapbox={
            "style": "open-street-map",
            "zoom": 14,
            "layers": [
                {
                    "source": json.loads(gdf.geometry.to_json()),
                    "below": "traces",
                    "type": "line",
                    "color": "red",
                    "line": {"width": 2.5},
                },
                                {
                    "source": json.loads(gtfs_gdf.geometry.to_json()),
                    "below": "traces",
                    "type": "circle",
                    "color": "blue",
                    "circle": {"radius": 2.5},
                }
            ],
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    ))
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
