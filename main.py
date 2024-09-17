import gradio as gr
from ilostat.ilostat import ILOStat

ilostat = ILOStat("en")

ilostat_areas = ilostat.get_areas()


with gr.Blocks() as demo:
    dataflows_dropdown = None
    areas_dropdown = gr.Dropdown(choices=ilostat_areas, label="Select an area")

    @gr.render(inputs=areas_dropdown)
    def get_dataflows(area):
        global dataflows_dropdown
        if area:
            dataflows = ilostat.get_dataflows(area)
            dataflows_dropdown = gr.Dropdown(
                choices=dataflows, label="Select a dataflow")

    @gr.render(inputs=dataflows_dropdown)
    def get_dataflow_description(something):
        print("bullshit")


if __name__ == "__main__":
    demo.launch()
