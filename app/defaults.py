from . import ilostat, default_area, default_dataflow
from .controller import AppController


class AppDefaults:
    """
    The DefaultSettings class encapsulates the initialization and configuration
    of data flows, dimensions, and related settings for a specified area
    and dataflow. This class retrieves dataflows, sets up dimensions, and
    prepares relevant data for further processing.

    Attributes:
        _area (str): The area for which dataflows and dimensions are defined.
        dataflow (str): The dataflow associated with the specified area.
        _dataflows (list): A list of available dataflows for the specified area.
        _dimensions (list): Dimensions for the specified area and dataflow.
        _current_dimensions (list): Initialized dimensions set for the current context.
        _data (any): Data retrieved or handled by `handle_get_data_button`.
    """

    def __init__(self, area=default_area, dataflow=default_dataflow):
        """
        Initializes the DefaultSettings object.

        Args:
            area (str, optional): The target area for dataflow retrieval.
                                  Defaults to the imported `default_area`.
            dataflow (str, optional): The target dataflow for the specified area.
                                      Defaults to the imported `default_dataflow`.
        """
        # Private attribute for the area
        self._area = area

        # Private attribute for the area label
        self._area_label = ilostat.get_area_label(area)

        # Fetch the full list of areas
        self._areas = ilostat.get_areas()

        # Dataflow for the specified area
        self._dataflow = dataflow

        # Fetch the dataflow label
        self._dataflow_label = ilostat.get_dataflow_label(dataflow)

        # Fetch dataflows associated with the specified area
        self._dataflows = ilostat.get_dataflows(area)

        # Retrieve dimensions for the specified area and dataflow
        self._dimensions = ilostat.get_area_dimensions(area, dataflow)

        # Instantiate a controller so we can use some of its methods to set defaults
        self._ctrl = AppController()

        # Initialize dimensions for current usage context
        self._current_dimensions = self._ctrl.init_current_dimensions(self._dimensions)

        # Handle data retrieval or preparation using a specific handler
        self._dataframe = self._ctrl.set_dataframe(
            area, dataflow, self._current_dimensions, None, None
        )

    @property
    def area(self):
        """
        Returns the area associated with the current settings.

        Returns:
            str: The area value.
        """
        return self._area

    @property
    def area_label(self):
        """
        Returns the area label for the specified area.

        Returns:
            str: The area label.
        """
        return self._area_label

    @property
    def areas(self):
        """
        Returns the area associated with the current settings.

        Returns:
            str: The area value.
        """
        return self._areas

    @property
    def dataflow(self):
        """
        Returns the dataflow associated with the current settings.

        Returns:
            str: The dataflow value.
        """
        return self._dataflow

    @property
    def dataflow_label(self):
        """
        Returns the dataflow label for the specified area.

        Returns:
            str: The dataflow label.
        """
        return self._dataflow_label

    @property
    def dataflows(self):
        """
        Returns the list of available dataflows for the specified area.

        Returns:
            list: List of dataflows.
        """
        return self._dataflows

    @property
    def dimensions(self):
        """
        Returns the dimensions for the specified area and dataflow.

        Returns:
            list: List of dimensions.
        """
        return self._dimensions

    @property
    def current_dimensions(self):
        """
        Returns the initialized current dimensions for use in this context.

        Returns:
            list: List of initialized dimensions.
        """
        return self._current_dimensions

    @property
    def dataframe(self):
        """
        Returns the data associated with the current configuration.

        Returns:
            any: The data object handled and retrieved during initialization.
        """
        return self._dataframe


if __name__ == "__main__":
    initial = AppDefaults()

    print("Initial area", initial.area)
    print("Initial dataflow", initial.dataflow)
    print("Number of dataflows", len(initial.dataflows))
    print("Dimensions", initial.dimensions)
    print("Current dimensions", initial.current_dimensions)
    print("Data", initial.dataframe)
