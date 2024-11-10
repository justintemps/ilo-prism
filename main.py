import gradio as gr
from app.handlers import (
    create_dimension_handler,
    set_dataflow,
    set_dimensions,
    init_current_dimensions,
    handle_get_data_button,
    get_areas,
    update_dataflow_label,
    render_chart,
)

# ===========================
# App Components
# ===========================

# UI components
title = gr.Markdown("# Summarize a table from ILOSTAT")

# Dropdown for geographic regions with dynamic choices
ilostat_areas = get_areas()

areas_dropdown = gr.Dropdown(
    choices=ilostat_areas, label="Select a geographic region", value=lambda: None
)

# Dropdown for dataflows (indicators) initialized as inactive
dataflows_dropdown = gr.Dropdown(
    label="Select an indicator from ILOSTAT", interactive=False
)

# Button to submit form data
get_data_button = gr.Button("Get data")


# Text area for displaying the output
output_dataframe = gr.Dataframe(label="Data will appear here")


with gr.Blocks(fill_height=True) as demo:

    # ===========================
    # Application State
    # ===========================

    # dataflow label
    dataflow_label = gr.State(None)

    # Dimensions available for the current Dataflow
    dimensions = gr.State(None)

    # The start year for the query
    start_year = gr.State(None)

    # The end year for the query
    end_year = gr.State(None)

    # The Dimensions currently selected by the user
    current_dimensions = gr.State({})

    # ===========================
    # App Rendering Section
    # ===========================

    # Render the app title
    title.render()

    # Layout using rows and columns for the UI components
    with gr.Row():

        # Left column for inputs
        with gr.Column():

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

                    with gr.Row():
                        # Render the rest of the dimensions
                        gr.Markdown("## Apply filters")

                    # First let's get the time period
                    time_period = next(
                        (dim for dim in dims if "TIME_PERIOD" in dim["dimension"]),
                        None,
                    )

                    # Let's remove it from the other dimensions so we can render it separately
                    if time_period:
                        dims.remove(time_period)

                        with gr.Row():
                            # Dropdown for starting year
                            start_year_dropdown = gr.Dropdown(
                                label="Select a starting year",
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
                                label="Select an ending year",
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
                        with gr.Row():
                            code, label = dimension["dimension"]
                            choices = dimension["values"]

                            handler = create_dimension_handler(code)

                            dimension_dropdown = gr.Dropdown(
                                label=label,
                                choices=choices,
                                interactive=True,
                                value=lambda: None,
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

            with gr.Tab("Data"):

                # Render text area for output display
                with gr.Row():
                    output_dataframe.render()

            with gr.Tab("Chart"):

                with gr.Row():

                    @gr.render(inputs=[output_dataframe, dataflow_label])
                    def render_vis(dataframe, dataflow_label):
                        render_chart(dataframe, dataflow_label)

    # ===========================
    # Component Event Handlers
    # ===========================

    # Event to populate dataflows based on selected area
    areas_dropdown.change(set_dataflow, areas_dropdown, dataflows_dropdown)

    # Event to set dimension details based on selected dataflow
    dataflows_dropdown.change(
        set_dimensions, [areas_dropdown, dataflows_dropdown], dimensions
    )

    dimensions.change(
        init_current_dimensions, inputs=dimensions, outputs=current_dimensions
    )

    # Event to handle submit button click, processing current dimensions and outputting results
    get_data_button.click(
        handle_get_data_button,
        inputs=[
            areas_dropdown,
            dataflows_dropdown,
            dataflow_label,
            current_dimensions,
            start_year,
            end_year,
        ],
        outputs=output_dataframe,
    )

    # Update the dataflow label but only when the dataframe is updated
    output_dataframe.change(
        update_dataflow_label, inputs=dataflows_dropdown, outputs=dataflow_label
    )


# ===========================
# Main Program Entry Point
# ===========================

if __name__ == "__main__":
    demo.launch()
