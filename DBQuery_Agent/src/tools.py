import matplotlib.pyplot as plt
from typing import List,Dict
import langchain_core.tools
import agentops.sdk.decorators
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import json


@langchain_core.tools.tool
@agentops.sdk.decorators.tool()
def text_listing_tool(data: List[str], title: str) -> str:
    """
    Generates a text file with a list of textual entries as bullet points.

    Use this tool when the SQL result returns only textual data (e.g., names of albums, artists, genres).
    
    Args:
        data (List[str]): A list of strings representing text records.
        title (str): A title or user query summarizing what the list represents.

    Returns:
        str: A formatted string with bullet points for each entry.

    Example: 
        Input:
            data = ["Black Album", "Master of Puppets"]
            title = "Albums by Metallica"

        Output:
            Albums by Metallica:
            • Black Album
            • Master of Puppets

    """
    print(title)
    dict_data = {title:data}
    with open("data.json","w") as f:
        json.dump(json.dumps(dict_data),f)
    # for i in data:
    #     print("* "+i)



@langchain_core.tools.tool
@agentops.sdk.decorators.tool()
def bar_chart_tool(data: Dict[str, float], title: str, x_axis: str, y_axis: str) -> str:
    '''
    Generates a bar chart from categorical-numeric pairs.

    Use this tool when the SQL result includes categories (e.g., countries, genres) with corresponding numeric values (e.g., revenue, sales count).

    Args:
        data (Dict[str, float]): Dictionary with category names as keys and numeric values as values.
        title (str): The user query used here as the title
        x_axis (str): Using state["sql_query_columns"][0] for the x-axis label (categorical like country,Name etc).
        y_axis (str): Using state["sql_query_columns"][1] for the y-axis (numerical like 37.87, 89, 98.2).

    Returns:
        str: Filepath of the plot.

    Example:
        Input:
            data = {"USA": 523.06, "India": 75.26}
            title = "Revenue by Country"
            x_axis = "Country"
            y_axis = "Revenue (USD)"
        
    '''
    plt.figure(figsize=(10,8))
    plt.bar(list(data.keys()), list(data.values()),width=0.3)
    plt.title(title)
    plt.xlabel(x_axis,fontweight='bold')
    plt.ylabel(y_axis,fontweight='bold')
    plt.xticks(rotation=90)
    save_path = "chart.png"
    plt.savefig(save_path)
    print('Plot Created')

    df = pd.DataFrame({x_axis:list(data.keys()),y_axis:list(data.values())})
    fig = go.Figure(px.bar(df, x=x_axis, y=y_axis))
    fig.update_layout(
        template='plotly_dark',  # stylish dark theme
        plot_bgcolor='#1f1f1f',  # background of plotting area
        paper_bgcolor='#111111',  # full canvas background
        font=dict(color='white', size=14),
        title=dict(
        text=f"<b>{title}</b>",
        font=dict(size=18),
        x=0.5  # Center the title
    )
    )
    fig.update_xaxes(tickangle=90)
    fig.write_image("chart2.png",width=1000, height=700, scale=2,format="png")
    #plt.show()

    ###create plotly graphing###

    return save_path



@langchain_core.tools.tool
@agentops.sdk.decorators.tool()
def line_chart_tool(data:Dict[str,float],x_axis:str,y_axis:str,title:str):
    '''
    Creates a line chart from time series data.

    Use this tool when the SQL result includes time-based keys (e.g., months, dates) and numeric values (e.g., monthly sales, revenue).

    Args:
        data (Dict[str, float]): Dictionary where keys are dates (format "YYYY-MM") and values are numeric.
        title (str): The user query used here as the title
        x_axis (str): Using state["sql_query_columns"][0] for the x-axis label (datetime in 'YYYY-MM').
        y_axis (str): Using state["sql_query_columns"][1] for the y-axis label (Numeric values like 38.98,89.98, 98).

    Returns:
        str: Filepath of the plot

    Example:
        Input:
            data = {"2022-01": 100.5, "2022-02": 110.2}
            title = "Monthly Revenue"
            x_axis = "Month"
            y_axis = "Revenue (USD)"
    
    '''
    plt.figure(figsize=(10,8))
    plt.plot(list(data.keys()), list(data.values()), linewidth=2)
    plt.xlabel(x_axis,fontweight='bold')
    plt.ylabel(y_axis,fontweight='bold')
    plt.title(title)
    save_path = "chart.png"
    plt.savefig(save_path)
    print('Plot Created')
    # plt.show()
    ### create plotly graphing ####
    df = pd.DataFrame({x_axis:list(data.keys()),y_axis:list(data.values())})
    # x_axis = x_axis.capitalize()
    # y_axis = y_axis.capitalize()
    fig = go.Figure(px.line(df, x=x_axis, y=y_axis))
    fig.update_layout(
        template='plotly_dark',  # stylish dark theme
        plot_bgcolor='#1f1f1f',  # background of plotting area
        paper_bgcolor='#111111',  # full canvas background
        font=dict(color='white', size=14),
        title=dict(
        text=f"<b>{title}</b>",
        font=dict(size=18),
        x=0.5  # Center the title
    )
    )
    fig.update_xaxes(tickangle=-90)
    fig.write_image("chart2.png",width=1000, height=700, scale=2,format="png")
    #fig.write_image("chart2.png",format="png") 


    #plt.show()

    return save_path