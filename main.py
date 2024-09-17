import gradio as gr
from ilostat.ilostat import ILOStat

ilostat = ILOStat("en")

areas = ilostat.get_areas()

with gr.Blocks() as demo:
    areas_dropdown = gr.Dropdown(
        choices=areas, label="Select an area")

if __name__ == "__main__":
    demo.launch()
