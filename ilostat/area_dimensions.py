import sdmx
from ._dsd import get_dsd


def find_dict_in_list(list_of_dicts, key, value):
    """
    Searches for and returns the first dictionary in a list of dictionaries
    where the specified key has a specified value. If no match is found, returns None.

    Parameters:
    - list_of_dicts (list): A list containing dictionaries.
    - key (str): The key to search for in each dictionary.
    - value: The value that the key should have.

    Returns:
    - dict or None: The first matching dictionary or None if no match is found.
    """
    for dictionary in list_of_dicts:
        if dictionary.get(key) == value:
            return dictionary
    return None


def filter_dimensions(data, filter_criteria):
    """
    Filters a list of data items based on specified dimension criteria.

    Parameters:
    - data (list): A list of data items, where each item is expected to be a dictionary
      with 'dimension' and 'values' keys.
    - filter_criteria (list): A list of dictionaries containing filter conditions, where
      each dictionary specifies a dimension and a list of allowed values.

    Returns:
    - list: A filtered list of data items that meet the specified criteria.
    """
    # Create a dictionary for easy access to filter values by dimension key
    filter_dict = {f["dimension"]: f["values"] for f in filter_criteria}

    # Initialize an empty list to store the filtered data items
    filtered_data = []

    for item in data:
        dimension_key = item["dimension"][0]  # Extract the dimension key from the item
        if dimension_key in filter_dict:
            # Filter values that match the filter criteria
            filtered_values = [
                value
                for value in item["values"]
                if value[1] in filter_dict[dimension_key]
            ]
            # Add items with matching values to the filtered list
            if filtered_values:
                filtered_data.append(
                    {"dimension": item["dimension"], "values": filtered_values}
                )

    return filtered_data


def filter_area_dimensions(area: str, dataflow: str, all_dimensions: any):
    """
    Retrieves dimensions for a dataflow available for a specified country/area.

    Parameters:
    - area (str): The country/area code to filter dimensions for (e.g., "ITA").
    - dataflow (str): The dataflow identifier for which dimensions are requested.
    - all_dimensions (list): A list of all available dimensions for the dataflow.

    Returns:
    - list: A filtered list of dimensions relevant to the specified country/area.
    """
    # Initialize a client to interact with ILO data services
    ilostat = sdmx.Client("ILO")

    # Retrieve the Data Structure Definition (DSD) for the specified dataflow
    dsd = get_dsd(ilostat, dataflow)

    # Set the area as the only dimension for filtering
    dimensions = {"REF_AREA": area}

    # Fetch data based on the area and dataflow
    data_msg = ilostat.data(
        dataflow,
        dsd=dsd,
        key=dimensions,
    )

    # Extract the list of observations from the fetched data
    observations = data_msg.data[0].obs

    # Initialize an empty list to store dimensions supported by the country/area
    area_dimensions = []

    # Define dimensions to exclude from filtering
    dimensions_to_exclude = ["REF_AREA"]

    for observation in observations:
        # Extract all dimension values for each observation
        all_obs_dimensions = observation.key.values

        # Create a new dictionary excluding dimensions that should not be filtered
        obs_dimensions = {
            key: value
            for key, value in all_obs_dimensions.items()
            if key not in dimensions_to_exclude
        }

        # Loop through remaining dimensions and build filtered dimension data
        for dimension in obs_dimensions:
            # Find existing dimension data or create a new one
            current_dim = find_dict_in_list(area_dimensions, "dimension", dimension)
            new_dim_value = obs_dimensions[dimension].value

            if not current_dim:
                # Add new dimension entry if not present
                new_dim = {
                    "dimension": dimension,
                    "values": {new_dim_value},
                }
                area_dimensions.append(new_dim)
                continue

            # Add new value to the existing dimension entry
            current_dim["values"].add(new_dim_value)

    # Filter dimensions using the gathered data
    filtered_dims = filter_dimensions(all_dimensions, area_dimensions)

    # The dimensions that we get from the dataflow metadat don't include time series.
    # We have to add those separately
    time_dimension = next(
        (dim for dim in area_dimensions if dim["dimension"] == "TIME_PERIOD"),
        None,
    )

    time_series = None

    # Format the time series dimension to be included in the results
    if time_dimension:
        time_series = {
            "dimension": ("TIME_PERIOD", "TIME_PERIOD"),
            "values": sorted(list(time_dimension["values"])),
        }
        filtered_dims.append(time_series)

    return filtered_dims


if __name__ == "__main__":
    from ._dimensions import get_dimensions

    # Example input parameters
    area = "ITA"  # Country/area code
    df = "DF_EAP_3EAP_SEX_AGE_DSB_NB"  # Dataflow identifier
    language = "en"  # Language code

    # Retrieve all dimensions for the specified dataflow
    all_dimensions = get_dimensions(df, language)

    # Filter dimensions for the specified area and dataflow
    dimensions = filter_area_dimensions(area, df, all_dimensions)

    # Display the filtered dimensions
    print(dimensions)
