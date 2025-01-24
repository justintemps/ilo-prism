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

            with gr.Tab("✨ AI Summary", interactive=True):
                chat_completion_textarea.render()
                get_chat_completion_button.render()

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

            with gr.Tab("💁 What's going on?"):
                gr.Markdown(
                    """
                    ## What is this?
                    This is a proof of concept for summarizing data from the [ILOSTAT SDMX API](https://ilostat.ilo.org/resources/sdmx-tools/) using a chat completion model.

                    ### How it works
                    1. **Select** a geographic region and an indicator from ILOSTAT.
                    2. **Filter** the data by choosing dimensions.
                    3. Click the **"Update data"** button to generate a prompt.
                    4. View a **chart** for a visual representation of the data.
                    5. Check the **"Prompt"** tab to see the generated prompt.
                    6. Go to the **"AI Summary"** tab and click **"Generate summary"** to create a summary using a chat completion model.

                    ### What problem does it solve?
                    Current large language models (LLMs) struggle with summarizing tabular data. These models are trained primarily on unstructured text, leaving them without a framework to understand two-dimensional data structures like tables. Moreover, they often lack the numerical reasoning skills required to interpret relationships between numbers in tables, such as trends over time.

                    This app addresses the problem by generating a prompt that distills key insights from tabular data, enabling a chat completion model to produce meaningful summaries.

                    ### What model is it using?
                    The app is compatible with any chat completion model capable of generating text from prompts. Testing with [Llama-3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) has yielded promising results. Further testing is needed to evaluate its performance with smaller models suitable for server hosting.

                    ### Why is this useful?
                    Text-based descriptions generated by this app can make data more accessible:
                    - They assist people with visual impairments or limited access to visual content by providing summaries of data.
                    - Combined with contextual information from news stories or reports, these summaries can help generate data-driven narratives, offering insights into complex labor and workplace issues.

                    ### What this isn't
                    This app is **not** a production-ready application. It’s a proof of concept showcasing how chat completion models can summarize data from ILOSTAT. It is not intended for deployment in production environments.

                    ### What's next?
                    - Combine this approach with a **Retrieval-Augmented Generation (RAG)** system to generate static pages for the ILO’s website, ilo.org.
                    - Use the same methodology to develop a **chatbot** providing an open interface to the ILO’s knowledge base, including its statistical resources.

                    ### Where’s the code?
                    The code for this app is available on [GitHub](https://github.com/justintemps/ilostat-simple-summarizer).

                    ### Who made this?
                    This app was created by [Justin Smith](https://github.com/justintemps), Senior Digital Communication Officer with the ILO Department of Communication and Public Information. It uses the [Gradio](https://gradio.app/) library for building interactive machine learning applications.

                    ### Acknowledgements
                    Special thanks to the ILOSTAT team, especially [Weichen Lee](https://github.com/wc-lei), for his support with the ILO SDMX API.
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
