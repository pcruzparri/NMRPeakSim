import dearpygui.dearpygui as dpg
import callbacks as cb
import asyncio
from nmrpeaksim.core import core
import numpy as np


dpg.create_context()
dpg.create_viewport(title='NMRPeakSim')
vpw = dpg.get_viewport_width()
vph = dpg.get_viewport_height()
spect_gui = {"width": vpw*2//3,
             "height": vph*2//3,
             "pos": (0, 0)}
peak_gui = {"width": vpw*2//3,
            "height": vph*1//3,
            "pos": (0, vph*2//3+20)}
options_gui = {"width": vpw*1//3-40,
               "height": vph*2//3,
               "pos": (vpw*2//3+20, 0)}
message_gui = {"width": vpw*1//3-40,
               "height": vph*1//3,
               "pos": (vpw*2//3+20, vph*2//3+20)}


spectrum = core.Plot()
peaks = []
selected_peak = 0

with dpg.window(tag='main_window'):
    # Plotting Spectrum
    with dpg.child_window(pos=spect_gui['pos'],
                          autosize_x=True,
                          tag='plot_window'):
        with dpg.plot(label='Spectrum View',
                      width=spect_gui['width'],
                      height=spect_gui['height'],
                      tag='main_plot'):
            dpg.add_plot_axis(dpg.mvXAxis, label='ppm', tag='spect_x_axis', invert=True)
            dpg.add_plot_axis(dpg.mvYAxis, label='Intensity', tag='spect_y_axis')
            dpg.add_line_series(spectrum.ppm, np.zeros(len(spectrum.ppm)),
                                tag='spectrum_line',
                                parent='spect_y_axis')
            dpg.set_axis_limits('spect_x_axis', 0, 10)
            dpg.add_plot_legend()

    # Plotting Peak
    with dpg.child_window(pos=peak_gui['pos'],
                          autosize_x=True,
                          autosize_y=True,
                          tag='peak_window'):
        with dpg.plot(label='Peak View',
                      width=peak_gui['width'],
                      tag='peak_plot'):
            dpg.add_plot_axis(dpg.mvXAxis, label='ppm', tag='peak_x_axis', invert=True)
            dpg.add_plot_axis(dpg.mvYAxis, label='Intensity', tag='peak_y_axis')
            dpg.add_line_series(spectrum.ppm, np.zeros(len(spectrum.ppm)),
                                tag='peak_line',
                                parent='peak_y_axis')

    # Tools
    with dpg.child_window(label="Tools",
                          width=options_gui['width'],
                          height=options_gui['height'],
                          pos=options_gui['pos'],
                          autosize_x=True,
                          autosize_y=True,
                          tag='tools_window'):
        with dpg.tab_bar(label='Tools'):

            # Peak Tab
            with dpg.tab(label='Peak'):
                dpg.add_combo(label='peak',
                              tag='peak_select',
                              user_data=(spectrum, peaks, selected_peak),
                              callback=cb.psu_wrapper)
                with dpg.group(tag='peak_creation'):
                    dpg.add_input_float(label="Shift (ppm)",
                                        default_value=5,
                                        tag='center_shift',
                                        width=150)
                    dpg.add_input_float(label="Integration",
                                      tag='integration',
                                      default_value=1,
                                      min_value=0,
                                      step=1,
                                      width=150)
                    dpg.add_input_int(label='Spectrometer Frequency (MHz)',
                                      default_value=300,
                                      step=10,
                                      step_fast=100,
                                      width=150,
                                      tag='field')
                    dpg.add_button(label="Create Peak",
                                   width=150,
                                   tag='add_peak',
                                   user_data=(spectrum, peaks, selected_peak),
                                   callback=cb.peak_creation_callback)
                dpg.add_spacer(height=20)

                with dpg.group(tag='peak_splitting'):
                    dpg.add_input_int(label='Multiplicity',
                                      default_value=2,
                                      width=150,
                                      tag='mult')
                    dpg.add_input_int(label='J Coupling (Hz)',
                                      default_value=15,
                                      width=150,
                                      tag='J')
                    dpg.add_button(label="Split Peak",
                                   width=150,
                                   user_data=(spectrum, peaks, selected_peak),
                                   tag='split_peak',
                                   callback=cb.peak_modify_callback)
                    dpg.add_button(label='Undo Split',
                                   width=150,
                                   user_data=(spectrum, peaks, selected_peak),
                                   tag='undo_split',
                                   callback=cb.peak_modify_callback)
                dpg.add_spacer(height=20)

                with dpg.group(tag='peak_shift'):
                    dpg.add_input_float(label='Delta (ppm)',
                                        width=150,
                                        tag='delta')
                    dpg.add_button(label='Shift Center',
                                   width=150,
                                   user_data=(spectrum, peaks, selected_peak),
                                   tag='shift_center',
                                   callback=cb.peak_modify_callback)
                dpg.add_spacer(height=20)

            dpg.add_tab(label='Spectrum')
            with dpg.tab(label='Plot'):
                pass


dpg.set_primary_window('main_window', True)
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    #cb.peak_select_update(spectrum, peaks, selected_peak)
    dpg.render_dearpygui_frame()

dpg.destroy_context()
