import gradio as gr
from ilostat.ilostat import ILOStat

ilostat = ILOStat("en")

areas = ilostat.get_areas()

with gr.Blocks() as demo:

    areas_dropdown = gr.Dropdown(
        areas.names, label="Select an area", default=areas.names[0])
