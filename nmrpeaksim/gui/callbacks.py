from nmrpeaksim.core.utils import *
import dearpygui.dearpygui as dpg
from icecream import ic


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
    dpg.delete_item(f'spect_line_{user_data.selected_peak}')
    for line in dpg.get_item_children('spect_y_axis', 1):
        line_ind = int(dpg.get_item_alias(line).strip('spect_line_'))
        if line_ind > user_data.selected_peak:
            dpg.set_item_alias(line, f'spect_line_{line_ind-1}')
    peak_select_update(sender, app_data, user_data)


def peak_modify_callback(sender, app_data, user_data):
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


def plot_callback_wrapper(sender, app_data, user_data):
    pass


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

        # update the peak labels
        if user_data.peaks != peak_labels:
            dpg.configure_item('peak_select', items=peak_labels)
            user_data.peaks = peak_labels

        # set selector to the last peak created
        if sender == 'add_peak':
            user_data.selected_peak = len(peak_labels)-1
            dpg.set_value('peak_select', peak_labels[-1])

        # handle when every peak is removed
        elif not peak_labels:
            user_data.selected_peak = None
            dpg.set_value('peak_select', '')
            update_spectrum_plot(user_data.spectrum)
            update_peak_plot(user_data.spectrum, ind=user_data.selected_peak)
            return

        # handle when an item is selected but it's label is no longer present or accurate
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

        update_spectrum_plot(user_data.spectrum)
        update_peak_plot(user_data.spectrum, ind=user_data.selected_peak, label=peak_labels[user_data.selected_peak])

    peak_info_update(user_data)
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
    peaks = spectrum.plot_all()
    for ind, peak in enumerate(peaks):
        if not dpg.does_item_exist(f'spect_line_{ind}'):
            dpg.add_line_series(*peak, parent='spect_y_axis', label=f'{ind}: {repr(spectrum.peaks[ind])}',
                                tag=f'spect_line_{ind}')
        else:
            dpg.set_value(f'spect_line_{ind}', peak)
            dpg.set_item_label(f'spect_line_{ind}', label=f'{ind}: {repr(spectrum.peaks[ind])}')
    dpg.fit_axis_data('spect_y_axis')


def spect_plot_params(sender, app_data, user_data):
    if sender == 'npts':
        user_data.spectrum.npts = app_data
        update_spectrum_plot(user_data.spectrum)
        update_peak_plot(user_data.spectrum,
                         user_data.selected_peak,
                         user_data.peaks[user_data.selected_peak])
    elif sender == 'spect_ppm_range':
        dpg.set_axis_limits('spect_x_axis', *app_data[:2])
    elif sender == 'spect_int_range':
        dpg.set_axis_limits('spect_y_axis', *app_data[:2])
    elif sender == 'fwhm':
        user_data.spectrum.fwhm = app_data
        update_spectrum_plot(user_data.spectrum)
        update_peak_plot(user_data.spectrum, ind=user_data.selected_peak, label=user_data.peaks[user_data.selected_peak])
    elif sender == 'fit_zoom':
        dpg.set_axis_limits_auto('spect_x_axis')
        dpg.set_axis_limits_auto('spect_y_axis')
        dpg.fit_axis_data('spect_x_axis')
        dpg.fit_axis_data('spect_y_axis')

def viewport_resize_callback(sender, app_data):
    vpw = app_data[2]
    vph = app_data[3]
    dpg.configure_item('peak_window', width=vpw*3//5, height=vph//2, pos=(0, 0))
    dpg.configure_item('tools_window', pos=(vpw*4//5, 0), height=vph//2)
    dpg.configure_item('plot_window', pos=(0, vph//2))
    dpg.configure_item('peak_info_window', width=vpw/5, height=vph/2, pos=(vpw*3//5, 0))
    dpg.configure_item('pwi_top', width=vpw//5, height=vph//4, pos=(0, 0))
    dpg.configure_item('pwi_bottom', width=vpw//5, height=vph//4, pos=(0, vph//2/2))


def peak_info_update(user_data):
    peak = user_data.spectrum.peaks[user_data.selected_peak]
    if len(peak.splittings) > 1:
        for ind, split in enumerate(peak.splittings[1:]):
            mult_default = get_key(mult_map, split)
            if not dpg.does_item_exist(f'split{ind+1}'):
                dpg.add_slider_int(label=f'J{ind+1},{split}',
                                   tag=f'split{ind+1}',
                                   default_value=mult_default,
                                   min_value=1,
                                   max_value=9,
                                   parent='pwi_top',
                                   width=150,
                                   user_data=user_data,
                                   callback=update_splitting_callback)
                dpg.add_slider_int(label=f'J{ind+1}',
                                   tag=f'coupling{ind+1}',
                                   default_value=peak.couplings[ind+1],
                                   max_value=50,
                                   parent='pwi_bottom',
                                   width=150,
                                   user_data=user_data,
                                   callback=update_coupling_callback)
            elif not dpg.is_item_shown(f'split{ind+1}'):
                dpg.show_item(f'split{ind+1}')
                dpg.show_item(f'coupling{ind+1}')
                dpg.set_value(f'split{ind+1}', mult_default)
                dpg.set_value(f'coupling{ind+1}', peak.couplings[ind+1])
    diff = len(peak.splittings[1:]) - len(dpg.get_item_children('pwi_top', 1)[2:])
    if diff < 0:
        for child in dpg.get_item_children('pwi_top', 1)[2:][diff:]:
            dpg.hide_item(child)
            dpg.hide_item('coupling'+dpg.get_item_alias(child).lstrip('split'))



def update_coupling_callback(sender, app_data, user_data):
    peak = user_data.spectrum.peaks[user_data.selected_peak]
    ind = sender.lstrip('coupling')
    mult = dpg.get_value('split'+sender.lstrip('coupling'))
    peak.change_splitting(ind=int(ind), mult=mult, J=app_data)

    update_peak_plot(user_data.spectrum, user_data.selected_peak, user_data.peaks[user_data.selected_peak])
    update_spectrum_plot(user_data.spectrum)
    peak_select_update(sender, None, user_data)


def update_splitting_callback(sender, app_data, user_data):
    peak = user_data.spectrum.peaks[user_data.selected_peak]
    ind = sender.lstrip('split')
    J = dpg.get_value('coupling'+sender.lstrip('split'))
    peak.change_splitting(ind=int(ind), mult=app_data, J=J)

    dpg.set_item_label(sender, f'J{ind},{mult_map[app_data]}')
    dpg.set_item_label('coupling'+sender.lstrip('split'), f'J{ind},{mult_map[app_data]}')

    update_peak_plot(user_data.spectrum, user_data.selected_peak, user_data.peaks[user_data.selected_peak])
    update_spectrum_plot(user_data.spectrum)
    peak_select_update(sender, None, user_data)
