import dearpygui.dearpygui as dpg
import callbacks as cb
import asyncio
from nmrpeaksim.core import core
import numpy as np


dpg.create_context()
dpg.create_viewport(title='NMRPeakSim')
dpg.set_viewport_resize_callback(cb.viewport_resize_callback)

class RunData:
    def __init__(self):
        self.spectrum = core.Plot()
        self.peaks = []
        self.selected_peak = 0

data = RunData()

with dpg.window(tag='main_window'):
    # Plotting Spectrum
    with dpg.child_window(width=-1,
                          height=-1,
                          tag='plot_window'):
        with dpg.plot(label='Spectrum View',
                      width=-1,
                      height=-1,
                      tag='main_plot'):
            dpg.add_plot_axis(dpg.mvXAxis, label='ppm', tag='spect_x_axis', invert=True)
            dpg.add_plot_axis(dpg.mvYAxis, label='Intensity', tag='spect_y_axis')
            dpg.set_axis_limits('spect_x_axis', 0, 10)
            dpg.add_plot_legend()

    # Plotting Peak
    with dpg.child_window(tag='peak_window'):
        with dpg.plot(label='Peak View',
                      width=-1,
                      height=-1,
                      tag='peak_plot'):
            dpg.add_plot_axis(dpg.mvXAxis, label='ppm', tag='peak_x_axis', invert=True)
            dpg.add_plot_axis(dpg.mvYAxis, label='Intensity', tag='peak_y_axis')
            dpg.add_line_series([], [], parent='peak_y_axis', tag='view_peak_line')

    # Plotting Peak Info
    with dpg.child_window(tag='peak_info_window',
                          no_scrollbar=True):
        dpg.add_child_window(tag='pwi_top')
        dpg.add_child_window(tag='pwi_bottom')

    # Tools
    with dpg.child_window(label="Tools",
                          width=-1,
                          autosize_x=True,
                          horizontal_scrollbar=True,
                          tag='tools_window'):
        with dpg.tab_bar(label='Tools'):

            with dpg.tab(label='Plot',
                         tag='plot_tab'):
                with dpg.group(tag='spectrum_plot_opts'):
                    dpg.add_input_int(label='Number of peak points',
                                      tag='npts',
                                      default_value=data.spectrum.npts,
                                      step_fast=1000,
                                      step=100,
                                      user_data=data,
                                      callback=cb.spect_plot_params,
                                      width=150)
                    dpg.add_input_floatx(label='Min/Max ppm',
                                         tag='spect_ppm_range',
                                         default_value=(data.spectrum.ppm_min, data.spectrum.ppm_max),
                                         size=2,
                                         user_data=data,
                                         callback=cb.spect_plot_params,
                                         width=150)
                    dpg.add_input_floatx(label='Min/Max intensity',
                                         tag='spect_int_range',
                                         size=2,
                                         default_value=(data.spectrum.intensity_min, data.spectrum.intensity_max),
                                         user_data=data,
                                         callback=cb.spect_plot_params,
                                         width=150)

            # Peak Tab
            with dpg.tab(label='Peak',
                         tag='peak_tab',
                         before='plot_tab'):
                with dpg.group(tag='peak_creation'):
                    dpg.add_input_float(label="Shift (ppm)",
                                        default_value=0.5,
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
                                   user_data=data,
                                   callback=cb.peak_creation_callback)
                dpg.add_button(label="Remove Peak",
                                  width=150,
                                   tag='remove_peak',
                                   user_data=data,
                                   callback=cb.peak_remove_callback)
                dpg.add_spacer(height=20)

                dpg.add_combo(label='Selected Peak',
                              tag='peak_select',
                              user_data=data,
                              callback=cb.peak_select_update,
                              width=150)
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
                                   user_data=data,
                                   tag='split_peak',
                                   callback=cb.peak_modify_callback)
                    dpg.add_button(label='Undo Split',
                                   width=150,
                                   user_data=data,
                                   tag='undo_split',
                                   callback=cb.peak_modify_callback)
                dpg.add_spacer(height=20)

                with dpg.group(tag='peak_shift'):
                    dpg.add_input_float(label='Delta (ppm)',
                                        width=150,
                                        tag='delta')
                    dpg.add_button(label='Shift Center',
                                   width=150,
                                   user_data=data,
                                   tag='shift_center',
                                   callback=cb.peak_modify_callback)
                dpg.add_spacer(height=20)




dpg.set_primary_window('main_window', True)
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()
