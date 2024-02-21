from nmrpeaksim.core.core import *
import dearpygui.dearpygui as dpg


def spect_gui_resize_callback():
    pass

def peak_creation_callback(sender, app_data, user_data):
    parent = dpg.get_item_parent(sender)
    kwargs = {dpg.get_item_alias(k): dpg.get_value(k) for k in dpg.get_item_children(parent)[1]
              if 'mvButton' != dpg.get_item_type(k).split('::')[1]}
    getattr(user_data[0], sender)(**kwargs)
    peak_select_update(*user_data)


def peak_modify_callback(sender, app_data, user_data):
    ind = peak_select_update(*user_data)[0]
    if sender == 'undo_split':
        getattr(user_data[0], 'modify')(ind, sender)
    else:
        parent = dpg.get_item_parent(sender)
        kwargs = {dpg.get_item_alias(k): dpg.get_value(k) for k in dpg.get_item_children(parent)[1]
                  if 'mvButton' != dpg.get_item_type(k).split('::')[1]}
        getattr(user_data[0], 'modify')(ind, sender, **kwargs)
    peak_select_update(*user_data)


def spectrum_callback(sender, app_data, user_data):
    pass


def plot_callback(sender, app_data, user_data):
    pass

'''
def peak_callback_wrapper(sender, _, user_data):
    if sender == 'create_peak':
        spectrum, method = user_data[:2]
        kwargs = {key: dpg.get_value(key) for key in user_data[2:]}
        getattr(spectrum, method)(**kwargs)
    else:
        spectrum, mod, ind, method = user_data[0:4]
        kwargs = {key: dpg.get_value(key) for key in user_data[4:]}
        getattr(spectrum, mod)(ind, method, **kwargs)
    dpg.set_value('spectrum_line', spectrum.plot(internal=False))
    dpg.set_value('peak_line', spectrum.plot(internal=False))
    print(spectrum.peaks)'''


def plot_callback_wrapper(sender, app_data, user_data):
    pass


def psu_wrapper(sender, app_data, user_data):
    peak_select_update(*user_data)


def peak_select_update(spectrum, peaks, selected_peak):
    peak_labels = [f'{ind}: {repr(pk)}' for ind, pk in enumerate(spectrum.peaks)]
    selected = dpg.get_value('peak_select')

    if peaks != peak_labels:
        dpg.configure_item('peak_select', items=peak_labels)
        peaks = peak_labels
        selected_peak = 0
        if selected:
            if selected != peak_labels[selected_peak]:
                selected_peak = int(dpg.get_value('peak_select').split(':')[0])
                dpg.set_value('peak_select', peak_labels[selected_peak])
        else:
            dpg.set_value('peak_select', peaks[selected_peak])
    update_peak_plot(spectrum, ind=selected_peak, label=peak_labels[selected_peak])
    update_spectrum_plot(spectrum)
    return selected_peak, peak_labels[selected_peak]


def update_peak_plot(spectrum, ind=0, label=''):
    peak = spectrum.plot_peak(peak_int=ind)
    dpg.set_value('view_peak_line', peak)
    dpg.configure_item('peak_plot', label=f'Peak View {label}')
    dpg.fit_axis_data('peak_y_axis')
    peak_x = dpg.get_value('view_peak_line')[0]
    dpg.set_axis_limits('peak_x_axis', peak_x[-1], peak_x[0])


def update_spectrum_plot(spectrum):
    dpg.delete_item('spect_y_axis', children_only=True)
    peaks = spectrum.plot_all()
    for ind, peak in enumerate(peaks):
        dpg.add_line_series(*peak, parent='spect_y_axis', label=f'{ind}: {repr(spectrum.peaks[ind])}')
    dpg.fit_axis_data('spect_y_axis')
