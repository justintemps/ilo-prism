import sdmx
from ._dsd import get_dsd


def find_dict_in_list(list_of_dicts, key, value):
    for dictionary in list_of_dicts:
        if dictionary.get(key) == value:
            return dictionary
    return None


def filter_dimensions(data, filter_criteria):
    # Create a dictionary to easily access filter values by dimension
    filter_dict = {f["dimension"]: f["values"] for f in filter_criteria}

    # Initialize an empty list to store the filtered data
    filtered_data = []

    for item in data:
        dimension_key = item["dimension"][0]  # Get the key for the dimension
        if dimension_key in filter_dict:
            # Filter values that match the criteria
            filtered_values = [
                value
                for value in item["values"]
                if value[1] in filter_dict[dimension_key]
            ]
            # If there are matching values, add to filtered data
            if filtered_values:
                filtered_data.append(
                    {"dimension": item["dimension"], "values": filtered_values}
                )

    return filtered_data


def filter_area_dimensions(area: str, dataflow: str, all_dimensions: any):
    """Gets the dimensions for a dataflow that area available for a specific country"""

    ilostat = sdmx.Client("ILO")

    # Get dsd
    dsd = get_dsd(ilostat, dataflow)

    # Set the area as the only dimension
    dimensions = {"REF_AREA": area}

    # Request the data
    data_msg = ilostat.data(
        dataflow,
        dsd=dsd,
        key=dimensions,
    )

    # Get the list of observations
    observations = data_msg.data[0].obs

    # The list of supported dimensions for this country and dataflow
    area_dimensions = []

    # The keys we don't need
    dimensions_to_exclude = ["REF_AREA", "TIME_PERIOD"]

    for observation in observations:

        # Get the dimensions for each observation
        all_obs_dimensions = observation.key.values

        # Create a new dict without the excluded keys
        obs_dimensions = {
            key: value
            for key, value in all_obs_dimensions.items()
            if key not in dimensions_to_exclude
        }

        # Loop through the remaining keys
        for dimension in obs_dimensions:

            current_dim = find_dict_in_list(area_dimensions, "dimension", dimension)

            new_dim_value = obs_dimensions[dimension].value

            if not current_dim:

                new_dim = {
                    "dimension": dimension,
                    "values": {new_dim_value},
                }

                area_dimensions.append(new_dim)

                continue

            current_dim["values"].add(new_dim_value)

    filtered_dims = filter_dimensions(all_dimensions, area_dimensions)

    return filtered_dims


if __name__ == "__main__":
    from ._dimensions import get_dimensions

    area = "ITA"
    df = "DF_EAP_3EAP_SEX_AGE_DSB_NB"
    language = "en"

    all_dimensions = get_dimensions(df, language)

    dimensions = filter_area_dimensions(area, df, all_dimensions)

    print(dimensions)
