import gradio as gr
from datetime import datetime
from . import ilostat


def get_areas():
    return ilostat.get_areas()


def set_dataflow(area):
    if area:
        dataflows = ilostat.get_dataflows(area)
        return gr.Dropdown(choices=dataflows, value=dataflows[0][1], interactive=True)
    return None


def set_description(dataflow):
    description = ilostat.get_dataflow_description(dataflow)
    return description


def set_dimensions(area, dataflow):
    if dataflow:
        dimensions = ilostat.get_area_dimensions(area=area, dataflow=dataflow)
        return dimensions
    return None


def init_current_dimensions(dims):
    dimensions = {}
    if dims:
        for dimension in dims:
            code, _ = dimension["dimension"]
            first_option = dimension["values"][0][1]
            dimensions[code] = first_option
    return dimensions


def create_dimension_handler(code: str):
    def set_current_dimension(current_dims: dict, new_dim: str):
        new_dims = current_dims
        new_dims[code] = new_dim
        return new_dims

    return set_current_dimension


def handle_submit_button(
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

    query = ilostat.query(dataflow=dataflow, dimensions=dimensions, params=params)

    result = query.data()

    return result
