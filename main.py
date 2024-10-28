import gradio as gr
from ilostat.ilostat import ILOStat
from app.handlers import (
    create_dimension_handler,
    set_dataflow,
    set_description,
    set_dimensions,
    init_current_dimensions,
    handle_submit_button,
    get_areas,
)

# ===========================
# App Components
# ===========================

# UI components
title = gr.Markdown("# Summarize a table from ILOSTAT")

# Dropdown for geographic regions with dynamic choices
ilostat_areas = get_areas()
areas_dropdown = gr.Dropdown(choices=ilostat_areas, label="Select a geographic region")

# Dropdown for dataflows (indicators) initialized as inactive
dataflows_dropdown = gr.Dropdown(
    label="Select an indicator from ILOSTAT", interactive=False
)

# Button to submit form data
submit_button = gr.Button("Get data")

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
        with gr.Column():

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
    dataflows_dropdown.change(set_dimensions, dataflows_dropdown, dimensions)

    # Event to initialize the current dimensions whenever dimensions change
    dimensions.change(
        init_current_dimensions, inputs=dimensions, outputs=current_dimensions
    )

    # Event to handle submit button click, processing current dimensions and outputting results
    submit_button.click(
        handle_submit_button,
        inputs=[areas_dropdown, dataflows_dropdown, current_dimensions],
        outputs=output_dataframe,
    )


# ===========================
# Main Program Entry Point
# ===========================

if __name__ == "__main__":
    demo.launch()
