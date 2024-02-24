from nmrpeaksim.core.core import *
import dearpygui.dearpygui as dpg


def spect_gui_resize_callback():
    pass

def peak_creation_callback(sender, app_data, user_data):
    parent = dpg.get_item_parent(sender)
    kwargs = {dpg.get_item_alias(k): dpg.get_value(k) for k in dpg.get_item_children(parent)[1]
              if 'mvButton' != dpg.get_item_type(k).split('::')[1]}
    getattr(user_data.spectrum, sender)(**kwargs)
    peak_select_update(sender, app_data, user_data)


def peak_remove_callback(sender, app_data, user_data):
    getattr(user_data.spectrum, sender)(user_data.selected_peak)
    peak_select_update(sender, app_data, user_data)


def peak_modify_callback(sender, app_data, user_data):
    print(peak_select_update(sender, app_data, user_data))
    ind = peak_select_update(sender, app_data, user_data)[0]
    if sender == 'undo_split':
        getattr(user_data.spectrum, 'modify')(ind, sender)
    else:
        parent = dpg.get_item_parent(sender)
        kwargs = {dpg.get_item_alias(k): dpg.get_value(k) for k in dpg.get_item_children(parent)[1]
                  if 'mvButton' != dpg.get_item_type(k).split('::')[1]}
        getattr(user_data.spectrum, 'modify')(ind, sender, **kwargs)
    peak_select_update(sender, app_data, user_data)


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


"""def psu_wrapper(sender, app_data, user_data):
    peak_select_update(user_data)

"""
def peak_select_update(sender, app_data, user_data):
    if sender == 'peak_select':
        if not app_data:
            user_data.selected_peak = 0
        else:
            user_data.selected_peak = int(app_data.split(':')[0])
        update_peak_plot(user_data.spectrum, ind=user_data.selected_peak, label=user_data.peaks[user_data.selected_peak])

    # Cases for creating, deleting, and modifying the peaks
    else:
        peak_labels = [f'{ind}: {repr(pk)}' for ind, pk in enumerate(user_data.spectrum.peaks)]
        selected = dpg.get_value('peak_select')
        print(peak_labels, selected)

        # update the peak labels
        if user_data.peaks != peak_labels:
            dpg.configure_item('peak_select', items=peak_labels)
            user_data.peaks = peak_labels

        if not peak_labels:
            user_data.selected_peak = None
            dpg.set_value('peak_select', '')
            update_peak_plot(user_data.spectrum, ind=user_data.selected_peak)
            update_spectrum_plot(user_data.spectrum)
            return

        elif selected and selected not in peak_labels:
            ind = int(selected.split(':')[0])
            if ind < len(peak_labels):
                user_data.selected_peak = ind
                dpg.set_value('peak_select', peak_labels[user_data.selected_peak])
            else:
                user_data.selected_peak = ind-1
                dpg.set_value('peak_select', peak_labels[user_data.selected_peak])

        else:
            if selected and selected != peak_labels[user_data.selected_peak]:
                user_data.selected_peak = int(dpg.get_value('peak_select').split(':')[0])
                dpg.set_value('peak_select', peak_labels[user_data.selected_peak])
            elif not selected and peak_labels:
                user_data.selected_peak = 0
                dpg.set_value('peak_select', user_data.peaks[user_data.selected_peak])

        update_peak_plot(user_data.spectrum, ind=user_data.selected_peak, label=peak_labels[user_data.selected_peak])
        update_spectrum_plot(user_data.spectrum)
    print(user_data.peaks, user_data.selected_peak)
    return user_data.selected_peak, user_data.peaks[user_data.selected_peak]


def update_peak_plot(spectrum, ind=0, label=''):
    if ind is None:
        dpg.set_value('view_peak_line', ((), ()))
        dpg.configure_item('peak_plot', label=f'Peak View')

    else:
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


def spect_plot_params(sender, app_data, user_data):
    if sender == 'npts':
        user_data.spectrum.npts = app_data
        update_spectrum_plot(user_data.spectrum)
        update_peak_plot(user_data.spectrum,
                         user_data.selected_peak,
                         user_data.peaks[user_data.selected_peak])
    elif sender == 'spect_int_range':
        pass
    elif sender == 'spect_int_range':
        pass

def viewport_resize_callback(sender, app_data):
    print(sender, app_data)
    vpw = app_data[2]
    vph = app_data[3]
    dpg.configure_item('peak_window', width=vpw*4//5, height=vph//2)
    dpg.configure_item('tools_window', pos=(vpw*4//5, 0), height=vph//2)
    dpg.configure_item('plot_window', pos=(0, vph//2))
