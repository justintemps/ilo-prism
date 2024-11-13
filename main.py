import gradio as gr
from app.defaults import DefaultSettings
from app.handlers import (
    create_dimension_handler,
    set_dataflow,
    set_dimensions,
    handle_get_data_button,
    get_areas,
    update_dataflow_label,
    render_chart,
    init_current_dimensions,
)
import pandas as pd

# ===========================
# Initialize defaults
# ===========================

initial = DefaultSettings()

# ===========================
# App Components
# ===========================

# UI components
title = gr.Markdown("# Summarize a table from ILOSTAT")

# Dropdown for geographic regions with dynamic choices
ilostat_areas = get_areas()
areas_dropdown = gr.Dropdown(
    choices=ilostat_areas, label="Select a geographic region", value=initial.area
)

# Dropdown for dataflows (indicators) initialized as inactive
dataflows_dropdown = gr.Dropdown(
    label="Select an indicator from ILOSTAT",
    value=initial.dataflow,
    choices=initial.dataflows,
)

dataflow_title = gr.Markdown("Choose a country")

dataflow_label = gr.Markdown("Choose an indicator")


# Output dataframe
output_dataframe = gr.DataFrame(value=initial.data)


# Button to submit form data
get_data_button = gr.Button("Update data")


with gr.Blocks(fill_height=True) as demo:

    # ===========================
    # Application State
    # ===========================

    # Dimensions available for the current Dataflow
    dimensions = gr.State(initial.dimensions)

    # The start year for the query
    start_year = gr.State(None)

    # The end year for the query
    end_year = gr.State(None)

    # The Dimensions currently selected by the user
    current_dimensions = gr.State(initial.current_dimensions)

    # ===========================
    # App Rendering Section
    # ===========================

    title.render()

    # Layout using rows and columns for the UI components
    with gr.Row():

        # Left column for inputs
        with gr.Column():

            gr.Markdown("## 🌍 Select a region and dataflow")

            # Render dropdown for area selection
            with gr.Row():
                areas_dropdown.render()

            # Render dropdown for dataflow selection
            with gr.Row():
                dataflows_dropdown.render()

            # Dynamically render dimension dropdowns based on selected dataflow

            @gr.render(inputs=dimensions)
            def render_dimensions(dims):

                if dims:

                    gr.Markdown("## 🔦 Filter the data")

                    with gr.Group():

                        with gr.Row():

                            # First let's get the time period
                            time_period = next(
                                (
                                    dim
                                    for dim in dims
                                    if "TIME_PERIOD" in dim["dimension"]
                                ),
                                None,
                            )

                            # Let's remove it from the other dimensions so we can render it separately
                            if time_period:
                                dims.remove(time_period)

                                # Dropdown for starting year
                                start_year_dropdown = gr.Dropdown(
                                    label="Starting year",
                                    choices=time_period["values"],
                                    value=time_period["values"][0],
                                    interactive=True,
                                )
                                start_year_dropdown.change(
                                    lambda year: year,
                                    inputs=start_year_dropdown,
                                    outputs=start_year,
                                )

                                # Dropdown for ending year
                                end_year_dropdown = gr.Dropdown(
                                    label="Ending year",
                                    choices=time_period["values"],
                                    value=time_period["values"][-1],
                                    interactive=True,
                                )
                                end_year_dropdown.change(
                                    lambda year: year,
                                    inputs=end_year_dropdown,
                                    outputs=end_year,
                                )

                        for dimension in dims:
                            code, label = dimension["dimension"]
                            choices = dimension["values"]

                            handler = create_dimension_handler(code)

                            dimension_dropdown = gr.Dropdown(
                                label=label,
                                choices=choices,
                                interactive=True,
                            )

                            dimension_dropdown.change(
                                handler,
                                inputs=[current_dimensions, dimension_dropdown],
                                outputs=current_dimensions,
                            )

            # Render the submit button
            get_data_button.render()

        # Right column for outputs
        with gr.Column(scale=2):

            dataflow_label.render()

            with gr.Tab("Data"):
                output_dataframe.render()

            with gr.Tab("Chart"):
                output_chart = gr.Plot()

                output_dataframe.change(
                    render_chart,
                    inputs=output_dataframe,
                    outputs=output_chart,
                )

    # ===========================
    # Component Event Handlers
    # ===========================

    # Event to populate dataflows based on selected area
    areas_dropdown.change(set_dataflow, areas_dropdown, dataflows_dropdown)

    # Event to set dimension details based on selected dataflow
    dataflows_dropdown.input(
        set_dimensions, [areas_dropdown, dataflows_dropdown], dimensions
    )

    # Initialize current dimensions when dimensions change
    dimensions.change(
        init_current_dimensions, inputs=dimensions, outputs=current_dimensions
    )

    # Event to handle submit button click, processing current dimensions and outputting results
    get_data_button.click(
        handle_get_data_button,
        inputs=[
            areas_dropdown,
            dataflows_dropdown,
            current_dimensions,
            start_year,
            end_year,
        ],
        outputs=output_dataframe,
    )

    # Update the dataflow label but only when the dataframe is updated
    output_dataframe.change(
        update_dataflow_label,
        inputs=[areas_dropdown, dataflows_dropdown],
        outputs=dataflow_label,
    )


# ===========================
# Main Program Entry Point
# ===========================

if __name__ == "__main__":
    demo.launch()
