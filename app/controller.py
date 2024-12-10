import gradio as gr
from ilostat.ilostat import ILOStat
from . import ilostat, default_client
from ._dim_controller import DimensionController
from .predict import AppPredictor
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Generator, Any, Tuple

# Set pandas options to avoid silent downcasting warnings when dealing with data types
pd.set_option("future.no_silent_downcasting", True)


class AppController:
    """
    The AppController class handles interactions with ILOSTAT data
    and creates components for a user interface using Gradio.
    It enables data querying, formatting, and visualization based on
    user-selected parameters such as area and dataflows.
    """

    def __init__(
        self, llm_client: AppPredictor = default_client, ilostat: ILOStat = ilostat
    ):
        """
        Initialize the AppController with an ILOStat instance.

        Parameters:
        - ilostat (ILOSTAT): The ILOSTAT instance for querying and retrieving data.
        """
        self._ilostat = ilostat
        self.dimension_controller = DimensionController
        self._llm_client = llm_client

    def set_dataflows(self, area: str):
        """
        Set and populate the dataflow dropdown based on the selected area.

        Parameters:
        - area (str): The selected geographic area.

        Returns:
        - gr.Dropdown: A Gradio dropdown populated with dataflows for the selected area.
        - None: If no area is selected.
        """
        if area:
            dataflows = self._ilostat.get_dataflows(area)
            return gr.Dropdown(choices=dataflows)
        return None

    def set_description(self, dataflow: str):
        """
        Retrieve and set the description for a given dataflow.

        Parameters:
        - dataflow (str): The dataflow for which to retrieve the description.

        Returns:
        - str: The description of the dataflow.
        """
        description = self._ilostat.get_dataflow_description(dataflow)
        return description

    def set_dimensions(self, area: str, dataflow: str):
        """
        Retrieve and set dimensions for a given area and dataflow.

        Parameters:
        - area (str): The selected geographic area.
        - dataflow (str): The selected dataflow.

        Returns:
        - list: List of dimensions for the specified area and dataflow.
        - None: If no dataflow is provided.
        """
        if dataflow:
            dimensions = self._ilostat.get_area_dimensions(area=area, dataflow=dataflow)
            return dimensions
        return None

    def init_current_dimensions(self, dimensions):
        """
        Initialize current dimensions with default values.

        Parameters:
        - dimensions (list): List of dimension dictionaries, each containing keys
          'dimension' and 'values'.

        Returns:
        - dict: A dictionary mapping dimension names to their default values.
        """
        current_dimensions = {}
        for dim in dimensions:
            key = dim["dimension"][0]  # Extract dimension key
            val = dim["values"][0][1]  # Extract default value
            current_dimensions[key] = val
        return current_dimensions

    def set_dataflow_label(self, area: str, dataflow: str):
        """
        Generate a formatted label for the selected area and dataflow.

        Parameters:
        - area (str): The selected geographic area.
        - dataflow (str): The selected dataflow.

        Returns:
        - str: Formatted label for display, or a placeholder if no values are provided.
        """
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

    def set_dataframe(
        self,
        area: str,
        dataflow: str,
        dimensions: dict[str, str],
        start_period: str,
        end_period: str,
    ):
        """
        Retrieve data as a DataFrame based on user-selected parameters.

        Parameters:
        - area (str): The selected geographic area.
        - dataflow (str): The selected dataflow.
        - dimensions (dict): A dictionary mapping dimension keys to their values.
        - start_period (str): The start period for data retrieval.
        - end_period (str): The end period for data retrieval.

        Returns:
        - pd.DataFrame: Data retrieved based on the provided parameters.
        """
        # Filter out keys with null or empty values from dimensions
        dimensions = {key: value for key, value in dimensions.items() if value}

        # Include the area if it's provided
        if area:
            dimensions["REF_AREA"] = area

        # Create query parameters excluding null values
        params = {
            key: value
            for key, value in {
                "startPeriod": start_period,
                "endPeriod": end_period,
            }.items()
            if value
        }

        # Execute the query with the specified parameters
        query = self._ilostat.query(
            dataflow=dataflow, dimensions=dimensions, params=params
        )
        result = query.data()

        return result

    def set_chart(self, df: pd.DataFrame):
        """
        Generate a chart based on a given DataFrame.

        Parameters:
        - df (pd.DataFrame): The data to be visualized.

        Returns:
        - gr.Plot: A Gradio plot object displaying the data.
        """
        if "value" in df.columns:
            # Replace empty strings with NaN for consistency
            df["value"] = df["value"].replace("", np.nan, regex=False)
            fig = plt.figure()

            # Set axis labels
            plt.xlabel("Time period")
            plt.ylabel(df["Measure"].iloc[0])

            # Group and plot data based on classification columns
            classifications = [col for col in df.columns if "classif" in col.lower()]
            for classification in classifications:
                for group_name, group_df in df.groupby(classification):
                    plt.plot(
                        group_df["TIME_PERIOD"], group_df["value"], label=group_name
                    )

            # Adjust layout for readability
            fig.autofmt_xdate()

            # Create the plot object before closing the figure
            plot = gr.Plot(value=fig)

            # Close the figure to free up memory
            plt.close(fig)

            return plot

    def chat_completion(
        self,
        area: str,
        dataflow: str,
        dataflow_description: str,
        df: pd.DataFrame,
    ) -> Generator[str | Any, Any, None]:
        dataflow_label = ilostat.get_dataflow_label(dataflow)
        area_label = ilostat.get_area_label(area)
        for response in self._llm_client.chat_completion(
            df=df,
            area_label=area_label,
            data_label=dataflow_label,
            data_description=dataflow_description,
        ):
            yield response

    def table_question_answering(
        self, area: str, dataflow: str, dataflow_description: str, df: pd.DataFrame
    ):

        response = self._llm_client.table_question_answering(
            df=df,
            area_label=area,
            data_label=dataflow,
            data_description=dataflow_description,
        )

        return response
