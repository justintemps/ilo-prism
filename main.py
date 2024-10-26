import gradio as gr
from ilostat.ilostat import ILOStat

# Setup ILOStat Client
ilostat = ILOStat("en")
ilostat_areas = ilostat.get_areas()

# Instantiate Gradio components

submit_button = gr.Button("Submit")

output_textara = gr.TextArea(
    label="Final output")

description_html = gr.HTML()


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


def create_dimension_dropdown_handler(code):
    def set_current_dimension(current_dims, new_dim):
        # Filter out any existing tuple with the same code
        current_dims = [(c, d) for c, d in current_dims if c != code]
        # Add the new tuple with the provided code and dimension
        return [*current_dims, (code, new_dim)]
    return set_current_dimension


def handle_submit_button(*args):
    if args:
        return ' '.join(map(str, args))


with gr.Blocks(fill_height=True) as demo:

    # Which dimensions are available for the dataflow
    dimensions = gr.State(None)

    # The currently selected dimensions
    current_dimensions = gr.State([])

    # Render the title
    gr.Markdown("# Summarize a table from ILOSTAT")

    with gr.Row():

        with gr.Column():

            with gr.Row():
                areas_dropdown = gr.Dropdown(
                    choices=ilostat_areas, label="Select a geographic region")

            with gr.Row():
                dataflows_dropdown = gr.Dropdown(
                    label="Select an indicator from ILOSTAT", interactive=False)

            @gr.render(inputs=dimensions)
            def render_dimensions(dims):
                if dims:
                    for dimension in dims:
                        with gr.Row():
                            code, label = dimension["dimension"]
                            choices = dimension["values"]

                            handler = create_dimension_dropdown_handler(code)

                            dimension_dropdown = gr.Dropdown(
                                label=label,
                                choices=choices,
                                interactive=True
                            )

                            dimension_dropdown.change(handler,
                                                      inputs=[
                                                          current_dimensions,
                                                          dimension_dropdown
                                                      ],
                                                      outputs=current_dimensions)

            submit_button.render()

        with gr.Column():

            with gr.Row():
                output_textara.render()

            with gr.Row():
                description_html.render()

    areas_dropdown.change(
        set_dataflow, areas_dropdown, dataflows_dropdown)

    dataflows_dropdown.change(
        set_description, dataflows_dropdown, description_html)

    dataflows_dropdown.change(set_dimensions,
                              dataflows_dropdown,
                              dimensions)

    dimensions.change(init_current_dimensions,
                      inputs=dimensions, outputs=current_dimensions)

    submit_button.click(handle_submit_button,
                        inputs=current_dimensions, outputs=output_textara)

if __name__ == "__main__":
    demo.launch()
