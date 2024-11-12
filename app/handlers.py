import gradio as gr
from . import ilostat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set pandas options to avoid silent downcasting
pd.set_option("future.no_silent_downcasting", True)


# Function to retrieve available areas
def get_areas():
    return ilostat.get_areas()


# Function to set the dataflow dropdown based on the selected area
def set_dataflow(area):
    if area:
        dataflows = ilostat.get_dataflows(area)
        return gr.Dropdown(choices=dataflows, interactive=True)
    return None


# Function to get and set a description for a dataflow
def set_description(dataflow):
    description = ilostat.get_dataflow_description(dataflow)
    return description


# Function to retrieve dimensions for a given area and dataflow
def set_dimensions(area, dataflow):
    if dataflow:
        dimensions = ilostat.get_area_dimensions(area=area, dataflow=dataflow)
        return dimensions
    return None


# Function factory to create a handler for updating dimensions
def create_dimension_handler(code: str):
    # Function to set a new value for a specific dimension
    def set_current_dimension(current_dims: dict, new_dim: str):
        new_dims = current_dims
        new_dims[code] = new_dim
        return new_dims

    return set_current_dimension


# Function to handle fetching data based on selected parameters
def handle_get_data_button(
    area: str,
    dataflow: str,
    dimensions: dict[str, str],
    start_period: str,
    end_period: str,
):
    # Filter out keys with null or empty values from dimensions
    dimensions = {key: value for key, value in dimensions.items() if value}

    # Only include area if it's not None or empty
    if area:
        dimensions["REF_AREA"] = area

    # Exclude keys with null values when creating params
    params = {
        key: value
        for key, value in {"startPeriod": start_period, "endPeriod": end_period}.items()
        if value
    }

    # Execute the query with the specified parameters
    query = ilostat.query(dataflow=dataflow, dimensions=dimensions, params=params)
    result = query.data()

    return result


# Function to update the label for a dataflow
def update_dataflow_label(area: str, dataflow: str):
    dataflow_label = ilostat.get_dataflow_label(dataflow)
    area_label = ilostat.get_area_label(area)

    placeholder = """
    ## Geographic region
    ### ILOSTAT Indicator
    """

    label = f"""
    ## {area_label}
    ### {dataflow_label}
    """

    if area and dataflow:
        return label

    return placeholder


def render_chart(df: pd.DataFrame):
    if "value" in df.columns:

        df["value"] = df["value"].replace("", np.nan, regex=False)
        fig = plt.figure()

        plt.xlabel("Time period")
        plt.ylabel(df["Measure"].iloc[0])

        classifications = [col for col in df.columns if "classif" in col.lower()]
        for classification in classifications:
            for group_name, group_df in df.groupby(classification):
                plt.plot(group_df["TIME_PERIOD"], group_df["value"], label=group_name)

        # Fix layout
        fig.autofmt_xdate()

        # Create the plot object before closing
        plot = gr.Plot(value=fig)

        # Close the figure after creating the plot object
        plt.close(fig)

        return plot


"""
Italy
Unemployment by sex, education and marital status
"""
