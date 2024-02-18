"""import matplotlib.pyplot as plt
from core.core import *
from core.utils import *

sf = 300

p = Peak(center_shift=6.21, integration=3)
p.split_peak(2, 3, ref=sf) #multiplicity, J in Hz
p.split_peak(2, 17.4, ref=sf)

plot = Plot()
plot.add_peak(peak=p)
plot.add_peak(center_shift=6, integration=2)
plot.modify(1, method='split_peak', mult=3, J=10, ref=sf)
plot.modify(1, method='split_peak', mult=2, J=15, ref=sf)

plot.custom_options(methods=[plt.xlim(7, 5)])
plot.plot()"""

import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Tutorial"):
    dpg.add_checkbox(label="Radio Button1", tag="R1")
    dpg.add_checkbox(label="Radio Button2", source="R1")

    dpg.add_input_text(label="Text Input 1")
    dpg.add_input_text(label="Text Input 2", source=dpg.last_item(), password=True)

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()