import gradio as gr
from app.defaults import AppDefaults
from app.controller import AppController

# ===========================
# Conroller & Default Classes
# ===========================

control = AppController()

initial = AppDefaults()

# ===========================
# App Components
# ===========================

# UI components
title = gr.Markdown("# Summarize a table from ILOSTAT")

# Dropdown for geographic regions with dynamic choices
areas_dropdown = gr.Dropdown(
    label="Select a geographic region", choices=initial.areas, value=initial.area
)

# Dropdown for dataflows (indicators) with dynamic choices
dataflows_dropdown = gr.Dropdown(
    label="Select an indicator from ILOSTAT",
    choices=initial.dataflows,
    value=initial.dataflow,
)

# Label for the selected dataflow
dataflow_label = gr.Markdown("")

# Description of the selected dataflow from ILOSTAT
dataflow_description = gr.HTML("Description goes here")

# Output dataframe
output_dataframe = gr.DataFrame(value=initial.dataframe)

# Button to submit form data
get_data_button = gr.Button("Update data")

# Button to generate chat completion
get_chat_completion_button = gr.Button("Start chat completion")

# Output textarea for chat completion
chat_completion_textarea = gr.TextArea(label="Click button to start chat completion")

# Ouput textarea for the prompt
prompt_textarea = gr.TextArea(label="The prompt for the model")


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

                            # handler = create_dimension_handler(code)
                            dimension_controller = control.dimension_controller(code)

                            dimension_dropdown = gr.Dropdown(
                                label=label,
                                choices=choices,
                                interactive=True,
                            )

                            dimension_dropdown.change(
                                dimension_controller.update,
                                inputs=[current_dimensions, dimension_dropdown],
                                outputs=current_dimensions,
                            )

            # Render the submit button
            get_data_button.render()

        # Right column for outputs
        with gr.Column(scale=2):

            dataflow_label.render()

            with gr.Tab("🔢 Data"):
                output_dataframe.render()

            with gr.Tab("📊 Chart"):
                output_chart = gr.Plot()

                output_dataframe.change(
                    control.set_chart,
                    inputs=output_dataframe,
                    outputs=output_chart,
                )

            with gr.Tab("📚 Metadata"):
                gr.Markdown("### Description of the data from ILOSTAT")
                dataflow_description.render()

            with gr.Tab("✍️ Prompt"):
                prompt_textarea.render()

            with gr.Tab("✨ Chat completion"):
                chat_completion_textarea.render()
                get_chat_completion_button.render()

    # ===========================
    # Component Event Handlers
    # ===========================

    # Event to populate dataflows based on selected area
    areas_dropdown.change(control.set_dataflows, areas_dropdown, dataflows_dropdown)

    # Event to set dimension details based on selected dataflow
    dataflows_dropdown.input(
        control.set_dimensions, [areas_dropdown, dataflows_dropdown], dimensions
    )

    # Initialize current dimensions when dimensions change
    dimensions.change(
        control.init_current_dimensions, inputs=dimensions, outputs=current_dimensions
    )

    # Event to handle submit button click, processing current dimensions and outputting results
    get_data_button.click(
        control.set_dataframe,
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
        control.set_dataflow_label,
        inputs=[areas_dropdown, dataflows_dropdown],
        outputs=dataflow_label,
    )

    # Update the dataflow description but only when the dataframe is updated
    output_dataframe.change(
        control.set_description,
        inputs=dataflows_dropdown,
        outputs=dataflow_description,
    )

    # Update the generated prompt but oly when the dataframe is updated
    output_dataframe.change(
        control.set_prompt,
        inputs=[
            areas_dropdown,
            dataflows_dropdown,
            dataflow_description,
            output_dataframe,
        ],
        outputs=prompt_textarea,
    )

    # Event to handle chat completion button click, processing the output dataframe and outputting summary
    get_chat_completion_button.click(
        fn=control.chat_completion,
        inputs=prompt_textarea,
        outputs=chat_completion_textarea,
    )


# ===========================
# Main Program Entry Point
# ===========================

if __name__ == "__main__":
    demo.launch()
