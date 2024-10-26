import gradio as gr
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


def set_dimensions(dataflow):
    if dataflow:
        dimensions = ilostat.get_dimensions(dataflow)
        return dimensions
    return None


def init_current_dimensions(dims):
    dimensions = []
    if dims:
        for dimension in dims:
            code, _ = dimension["dimension"]
            first_option = dimension["values"][0][1]
            dimensions.append((code, first_option))
    return dimensions


def create_dimension_handler(code):
    def set_current_dimension(current_dims, new_dim):
        # Filter out any existing tuple with the same code
        current_dims = [(c, d) for c, d in current_dims if c != code]
        # Add the new tuple with the provided code and dimension
        return [*current_dims, (code, new_dim)]

    return set_current_dimension


def handle_submit_button(dimensions):
    return str(dimensions)
