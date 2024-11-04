import gradio as gr
from app.handlers import (
    create_dimension_handler,
    set_dataflow,
    set_description,
    set_dimensions,
    init_current_dimensions,
    handle_submit_button,
    get_areas,
    get_last_20_years,
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

# Last 20 years
last_20_years = get_last_20_years()

# Dropdown for starting year
start_year_dropdown = gr.Dropdown(
    label="Select a starting year",
    choices=last_20_years,
    value=last_20_years[10],
    interactive=True,
)

# Dropdown for starting year
end_year_dropdown = gr.Dropdown(
    label="Select an ending year",
    choices=last_20_years,
    value=last_20_years[-1],
    interactive=True,
)

# Button to submit form data
submit_button = gr.Button("Get data")

# Line plot for displaying the output
# TODO: This doesn't work yet because of a bug in Gradio
# output_lineplot = gr.LinePlot(y="value", x="TIME_PERIOD")

# Text area for displaying the output
output_dataframe = gr.Dataframe(label="Final output")

# HTML component to display dynamic descriptions
description_html = gr.HTML()

with gr.Blocks(fill_height=True) as demo:

    # ===========================
    # Application State
    # ===========================

    # Dimensions available for the current Dataflow
    dimensions = gr.State(None)

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

            with gr.Row():

                start_year_dropdown.render()

                end_year_dropdown.render()

            # Dynamically render dimension dropdowns based on selected dataflow
            @gr.render(inputs=dimensions)
            def render_dimensions(dims):
                if dims:
                    for dimension in dims:
                        with gr.Row():
                            code, label = dimension["dimension"]
                            choices = dimension["values"]

                            handler = create_dimension_handler(code)

                            dimension_dropdown = gr.Dropdown(
                                label=label, choices=choices, interactive=True
                            )

                            dimension_dropdown.change(
                                handler,
                                inputs=[current_dimensions, dimension_dropdown],
                                outputs=current_dimensions,
                            )

            # Render the submit button
            submit_button.render()

        # Right column for outputs
        with gr.Column(scale=2):

            # Render the line plot for output display
            # TODO: This doesn't work yet because of a bug in Gradio

            # with gr.Row():
            # output_lineplot.render()

            # Render text area for output display
            with gr.Row():
                output_dataframe.render()

            # Render HTML for description display
            with gr.Row():
                description_html.render()

    # ===========================
    # Component Event Handlers
    # ===========================

    # Event to populate dataflows based on selected area
    areas_dropdown.change(set_dataflow, areas_dropdown, dataflows_dropdown)

    # Event to update description based on selected dataflow
    dataflows_dropdown.change(set_description, dataflows_dropdown, description_html)

    # Event to set dimension details based on selected dataflow
    dataflows_dropdown.change(
        set_dimensions, [areas_dropdown, dataflows_dropdown], dimensions
    )

    dimensions.change(
        init_current_dimensions, inputs=dimensions, outputs=current_dimensions
    )

    # Event to handle submit button click, processing current dimensions and outputting results
    submit_button.click(
        handle_submit_button,
        inputs=[
            areas_dropdown,
            dataflows_dropdown,
            current_dimensions,
            start_year_dropdown,
            end_year_dropdown,
        ],
        outputs=output_dataframe,
    )

    # Event to initialize the current dimensions whenever dimensions change
    # TODO: This doesn't work yet because of a bug in Gradio
    # output_dataframe.change(lambda x: x, output_dataframe, output_lineplot)


# ===========================
# Main Program Entry Point
# ===========================

if __name__ == "__main__":
    demo.launch()
