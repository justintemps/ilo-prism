import gradio as gr
from ilostat.ilostat import ILOStat

ilostat = ILOStat("en")

ilostat_areas = ilostat.get_areas()


with gr.Blocks() as demo:

    # Render the title
    gr.Markdown("# Summarize a table from ILOSTAT")

    # Which area to query data about
    query_area = gr.State(None)

    # Which dataflows to query
    query_dataflow = gr.State(None)

    # Areas dropdown menu
    areas_dropdown = gr.Dropdown(
        choices=ilostat_areas, label="First select a geographic region")

    # Update the query_area state on change
    areas_dropdown.input(
        lambda area: area, areas_dropdown, query_area)

    @gr.render(inputs=[query_area, query_dataflow])
    def render_dataflows(area, df):
        # Once we select an area, now we can render the dataflows
        if area:
            dataflows = ilostat.get_dataflows(area)
            dataflows_dropdown = gr.Dropdown(
                choices=dataflows, label="Then select an indicator from ILOSTAT", value=df)
            dataflows_dropdown.change(
                lambda df: df, dataflows_dropdown, query_dataflow)

    @gr.render(inputs=[query_area, query_dataflow])
    def render_dimensions(area, df):
        # Once we select the dataflows, now we can show the description
        if df and len(df) > 0:

            # Everything from here on down is borked
            description = ilostat.get_dataflow_description(df)
            dimensions = ilostat.get_dimensions(df)
            dimension_dropdown = {}
            dimension_dropdowns = []
            dimension_state = gr.State(value={})

            def update_dynamic_state(*args):
                return "bullshit"

            gr.Markdown("## Select dimensions")
            for dimension in dimensions:
                code, label = dimension["dimension"]

                dimension_dropdown[code] = gr.Dropdown(key=code,
                                                       label=label,
                                                       choices=dimension["values"])

                dimension_dropdowns.append(dimension_dropdown[code])

                dimension_dropdown[code].input(
                    update_dynamic_state, outputs=dimension_state)

            gr.Markdown("## About this data")
            gr.HTML(description)


if __name__ == "__main__":
    demo.launch()
