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
title = gr.Markdown("# <center>🤖 ILOSTAT Simple Summarizer</center>")

subtitle = gr.Markdown(
    "## <center>A proof of concept for summarizing ILOSTAT data using chat completion models</center>"
)

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


# Description of the selected dataflow from ILOSTAT
dataflow_description = gr.HTML("Description goes here")

# Output dataframe
output_dataframe = gr.DataFrame(value=initial.dataframe)

# Button to submit form data
get_data_button = gr.Button("Update data")

# Button to generate chat completion
get_chat_completion_button = gr.Button("Generate summary")

# Output textarea for chat completion
chat_completion_textarea = gr.TextArea()

# Ouput textarea for the prompt
prompt_markdown = gr.Markdown(label="The prompt for the model")


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
    subtitle.render()
    gr.Markdown("---")

    # Layout using rows and columns for the UI components
    with gr.Row():

        # Left column for inputs
        with gr.Column():

            gr.Markdown("### 🌍 Select a region and dataflow")

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

                    gr.Markdown("### 🔦 Filter the data")

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
                prompt_markdown.render()

            with gr.Tab("✨ AI Summary", interactive=True):
                chat_completion_textarea.render()
                get_chat_completion_button.render()

            with gr.Tab("💁 What's going on?"):
                gr.Markdown(
                    """
                    ## What is this?
                    This is a proof of concept for summarizing data from the [ILOSTAT SDMX API](https://ilostat.ilo.org/resources/sdmx-tools/) using a chat completion model.

                    ### How it works
                    1. Select a geographic region and an indicator from ILOSTAT.
                    2. Filter the data by selecting dimensions.
                    3. Click the "Update data" button to generate a prompt.
                    4. See the chart for a visual representation of the data.
                    5. Go to the "Prompt" tab to see the generated prompt.
                    6. Go to the "AI Summary" tab and click the "Generate summary" button to generate a summary using a chat completion model.

                    ### What problem does it solve?
                    Current large language models (LLMs) struggle with summarising tabular data. They're trained entirely on unstructured text and have no framework for understanding two-dimensional data structures like tables. They also lack the numerical reasoning skills that are needed to understand the relationships between numbers in a table, from the values themselves to the time periods they represent. This app proposes a solution to this problem by distilling key insights from tabular data into a prompt that can be used to generate a summary using a chat completion model.

                    ### What model is it using?
                    This app will work with any chat completion model that can generate text based on a prompt. [Llama-3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) was tested with good results. More testing is needed to determine if the app works as well with smaller models that can be hosted on a server.

                    ### Why is this useful?
                    Text descriptions like the ones generated here can be used to generate accessible summaries of data for people with seeing disabilities or limited access to visual content. Together with contextual information from news stories or reports, they can also be used to generate data-driven narratives that help people understand complex world of work issues.

                    ### What this isn't
                    A production-ready application. This is a proof of concept that demonstrates how chat completion models can be used to summarize data from ILOSTAT. It is not intended for use in production environments.

                    ### What's next?
                    - A similar approach could be combined with a Retrieval Augmented Generation (RAG) system to generate static pages for the ILO's website ilo.org
                    - The same thing could be used to build a chatbot providing an open interface for the ILO's knowledge base, with full access to its statistical resources.

                    ## Where's the code?
                    The code for this app is available on [GitHub](https://github.com/justintemps/ilo-prism)

                    ### Who made this
                    This app was created by [Justin Smith](https://github.com/justintemps), Senior Digital Communication Officer with the ILO Department of Communication and Public Information. It uses the [Gradio](https://gradio.app/) library for building interactive machine learning applications.

                    ### Acknowledgements
                    Many thanks to the ILOSTAT team, especially [Weichen Lee](https://github.com/wc-lei), for his support using the ILO SDMX API.
                    """
                )

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
            output_dataframe,
        ],
        outputs=prompt_markdown,
    )

    # Event to handle chat completion button click, processing the output dataframe and outputting summary
    get_chat_completion_button.click(
        fn=control.chat_completion,
        inputs=prompt_markdown,
        outputs=chat_completion_textarea,
    )


# ===========================
# Main Program Entry Point
# ===========================

if __name__ == "__main__":
    demo.launch()
