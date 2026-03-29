from collections import defaultdict
from nmrpeaksim.core.utils import *
import dearpygui.dearpygui as dpg

# Set by main() so viewport_resize_callback can trigger a tree redraw.
_run_data = None


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
            update_tree_diagram(user_data)
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
    update_tree_diagram(user_data)
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


def update_tree_diagram(user_data):
    """Render the coupling tree diagram for the currently selected peak."""
    dpg.delete_item('tree_canvas', children_only=True)

    canvas_w = dpg.get_item_width('tree_canvas')
    canvas_h = dpg.get_item_height('tree_canvas')

    # ── Title (always drawn) ──────────────────────────────────────────────────
    title_text = 'Coupling Tree'
    dpg.draw_text([canvas_w / 2 - len(title_text) * 4.5, 4],
                  title_text, color=[200, 200, 200, 230], size=16, parent='tree_canvas')

    if user_data.selected_peak is None or not user_data.spectrum.peaks:
        dpg.draw_text([10, 34], 'No peak selected',
                      color=[140, 140, 140, 200], size=18, parent='tree_canvas')
        return

    peak = user_data.spectrum.peaks[user_data.selected_peak]
    intensities = peak.intensities
    subpeak_shifts = peak.subpeak_shifts
    splittings = peak.splittings
    couplings = peak.couplings
    n_levels = len(intensities)

    margin_x  = 12
    margin_top = 28   # clearance above the topmost line tip (includes title)
    axis_h    = 38    # fixed pixels reserved at the bottom for the Hz number line
    label_col_w = 140  # right-side column for level labels

    draw_w = canvas_w - label_col_w

    # ── X-axis: singlet always centered; axis expands smoothly but slower than peaks
    center_ppm = peak.center_shift
    center_x   = draw_w / 2

    all_shifts_flat = [s for level in subpeak_shifts for s in level]
    actual_max_hz   = max(abs(s - center_ppm) * peak.field for s in all_shifts_flat)

    # axis_bound grows proportionally (×1.2) plus a fixed 5 Hz cushion.
    # This means the axis always lags behind the peaks — peaks visibly move
    # outward as J increases, while the axis also expands but more slowly.
    axis_bound_hz = actual_max_hz * 1.2 + 5

    scale_px = (draw_w / 2 - margin_x) / (axis_bound_hz / peak.field)

    def ppm_to_x(ppm):
        # NMR convention: high ppm → left
        return center_x - (ppm - center_ppm) * scale_px

    # ── Y-axis row layout ─────────────────────────────────────────────────────
    # The drawable band (for lines + edges) runs from (margin_top + line_h) to
    # (canvas_h - axis_h).  That way:
    #   • level 0's line tip is exactly at margin_top  (fully visible)
    #   • level N-1's baseline sits at the top of the axis area
    # We choose line_h first (fixed), then derive row spacing from what remains.

    draw_band_h = canvas_h - axis_h - margin_top   # total px for lines + gaps
    # line_h: ~22 % of the band, capped so it never exceeds half the band
    line_h = min(draw_band_h * 0.22, 70)

    # Baselines: span from (margin_top + line_h) down to (canvas_h - axis_h)
    y_first = margin_top + line_h          # baseline of level 0
    y_last  = canvas_h  - axis_h           # baseline of last level

    def level_to_y(lvl):
        if n_levels == 1:
            return (y_first + y_last) / 2
        return y_first + lvl * (y_last - y_first) / (n_levels - 1)

    LEVEL_COLORS = [
        [210, 210, 210, 255],   # grey   — singlet
        [100, 180, 255, 255],   # blue   — 1st split
        [80,  220, 130, 255],   # green  — 2nd split
        [255, 200,  70, 255],   # yellow — 3rd split
        [255, 100, 100, 255],   # red    — 4th split
        [200, 100, 255, 255],   # purple — 5th split
    ]
    EDGE_COLOR = [140, 140, 140, 160]

    # ── Vertical gridlines at major tick positions (drawn first, in background) ─
    if axis_bound_hz <= 10:
        tick_hz = 2
    elif axis_bound_hz <= 25:
        tick_hz = 5
    elif axis_bound_hz <= 50:
        tick_hz = 10
    else:
        tick_hz = 25

    GRID_COLOR = [70, 70, 70, 120]
    t = 0.0
    while t <= axis_bound_hz * 1.05:
        for hz_val in ([0.0] if t == 0 else [t, -t]):
            tx = ppm_to_x(center_ppm + hz_val / peak.field)
            if margin_x <= tx <= draw_w - margin_x:
                dpg.draw_line([tx, margin_top], [tx, canvas_h - axis_h],
                              color=GRID_COLOR, thickness=1.0, parent='tree_canvas')
        t = tick_hz if t == 0 else t + tick_hz

    # ── Edges: base of parent → tip of child ─────────────────────────────────
    for level in range(n_levels - 1):
        n_par = len(subpeak_shifts[level])
        mult  = len(subpeak_shifts[level + 1]) // n_par
        for pi in range(n_par):
            px = ppm_to_x(subpeak_shifts[level][pi])
            py = level_to_y(level)                    # base of parent
            for k in range(mult):
                ci = pi * mult + k
                cx = ppm_to_x(subpeak_shifts[level + 1][ci])
                cy = level_to_y(level + 1) - line_h   # tip of child
                dpg.draw_line([px, py], [cx, cy],
                              color=EDGE_COLOR, thickness=2.0, parent='tree_canvas')

    # ── Vertical lines and right-side level labels ────────────────────────────
    # Subpeaks that land on the same pixel are drawn as a single thicker line,
    # with thickness proportional to their combined intensity.
    BASE_THICKNESS = 3.5
    for level in range(n_levels):
        color  = LEVEL_COLORS[level % len(LEVEL_COLORS)]
        y_base = level_to_y(level)

        # Group subpeaks by rounded pixel x — detect overlaps
        px_groups  = defaultdict(float)   # px_key → summed intensity
        px_x_exact = {}                   # px_key → first exact x position
        for node_idx in range(len(subpeak_shifts[level])):
            x      = ppm_to_x(subpeak_shifts[level][node_idx])
            px_key = round(x)
            px_groups[px_key]  += intensities[level][node_idx]
            if px_key not in px_x_exact:
                px_x_exact[px_key] = x

        min_int = min(intensities[level])
        for px_key, total_intensity in px_groups.items():
            x         = px_x_exact[px_key]
            thickness = BASE_THICKNESS * total_intensity / min_int
            # TODO: for high multiplets (sextet+) the proportional thickness makes even
            # non-overlapping lines hard to distinguish. Consider an alternative encoding
            # (e.g. color opacity, a small numeric intensity label, or a variable-height
            # bar chart style) so individual subpeaks remain visually separable.
            dpg.draw_line([x, y_base], [x, y_base - line_h],
                          color=color, thickness=thickness, parent='tree_canvas')

        lbl = 's' if level == 0 else f'{splittings[level]},  J = {int(couplings[level])} Hz'
        dpg.draw_text([draw_w + 6, y_base - line_h / 2 - 8],
                      lbl, color=color, size=16, parent='tree_canvas')

    # ── Hz markers: centred on child lines, stacked vertically if they overlap ──
    V_GAP = 24   # px between stacked rows of arrows

    for level in range(1, n_levels):
        color = LEVEL_COLORS[level % len(LEVEL_COLORS)]
        n_par = len(subpeak_shifts[level - 1])
        mult  = len(subpeak_shifts[level]) // n_par
        if mult < 2:
            continue

        # Midpoint of each child vertical line
        y_mid = level_to_y(level) - line_h / 2

        # Collect (xa, xb) for every adjacent pair within the same parent group
        # xa < xb in pixel space (xa is further left = higher ppm)
        pairs = []
        for pi in range(n_par):
            for k in range(mult - 1):
                xa = ppm_to_x(subpeak_shifts[level][pi * mult + k])
                xb = ppm_to_x(subpeak_shifts[level][pi * mult + k + 1])
                if xa > xb:
                    xa, xb = xb, xa
                pairs.append((xa, xb))

        # Greedy interval-scheduling: assign each pair to the first row where it
        # doesn't overlap with the already-placed rightmost marker.
        sort_idx  = sorted(range(len(pairs)), key=lambda i: pairs[i][0])
        row_of    = [0] * len(pairs)
        rows_right = []   # tracks rightmost xb placed in each row

        for i in sort_idx:
            xa, xb = pairs[i]
            placed = False
            for ri, right in enumerate(rows_right):
                if xa > right + 2:          # 2 px gap to avoid touching
                    rows_right[ri] = xb
                    row_of[i] = ri
                    placed = True
                    break
            if not placed:
                row_of[i] = len(rows_right)
                rows_right.append(xb)

        n_rows = len(rows_right)

        for i, (xa, xb) in enumerate(pairs):
            # Distribute rows symmetrically around y_mid
            y = y_mid + (row_of[i] - (n_rows - 1) / 2) * V_GAP

            dpg.draw_arrow([xb, y], [xa, y],
                           color=color, thickness=1.5, size=7, parent='tree_canvas')
            dpg.draw_arrow([xa, y], [xb, y],
                           color=color, thickness=1.5, size=7, parent='tree_canvas')

            marker_lbl = f'{int(couplings[level])} Hz'
            lx = (xa + xb) / 2 - len(marker_lbl) * 4
            dpg.draw_text([lx, y - 16],
                          marker_lbl, color=color, size=15, parent='tree_canvas')

    # ── Hz number line — pinned to the bottom, fixed to axis_bound_hz ───────────
    y_axis = canvas_h - axis_h // 2
    # tick_hz already computed above for the gridlines

    dpg.draw_line([margin_x, y_axis], [draw_w - margin_x, y_axis],
                  color=[170, 170, 170, 210], thickness=2.0, parent='tree_canvas')
    dpg.draw_text([draw_w - margin_x + 4, y_axis - 8],
                  'Hz', color=[160, 160, 160, 230], size=14, parent='tree_canvas')

    t = 0.0
    while t <= axis_bound_hz + 0.01:
        for hz_val in ([0.0] if t == 0 else [t, -t]):
            tx = ppm_to_x(center_ppm + hz_val / peak.field)
            if margin_x <= tx <= draw_w - margin_x:
                dpg.draw_line([tx, y_axis - 6], [tx, y_axis + 6],
                              color=[170, 170, 170, 210], thickness=2.0, parent='tree_canvas')
                lbl = '0' if hz_val == 0 else f'{hz_val:g}'
                dpg.draw_text([tx - len(lbl) * 4, y_axis + 8],
                              lbl, color=[160, 160, 160, 230], size=13, parent='tree_canvas')
        t = tick_hz if t == 0 else t + tick_hz


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

    top_h        = vph // 2
    peak_info_w  = 240          # fixed — wide enough for title text + 150 px sliders
    tools_w      = vpw // 5     # tools panel stays proportional

    # Peak view and coupling tree equally share whatever is left of the top half
    left_pair_total = vpw - peak_info_w - tools_w
    half_left_w     = left_pair_total // 2

    dpg.configure_item('peak_window', width=half_left_w, height=top_h, pos=(0, 0))
    dpg.configure_item('tree_window', width=half_left_w, height=top_h, pos=(half_left_w, 0))
    dpg.configure_item('tree_canvas', width=half_left_w - 16, height=top_h - 16)

    dpg.configure_item('peak_info_window', width=peak_info_w, height=top_h, pos=(left_pair_total, 0))
    dpg.configure_item('pwi_top',    width=peak_info_w, height=top_h // 2, pos=(0, 0))
    dpg.configure_item('pwi_bottom', width=peak_info_w, height=top_h // 2, pos=(0, top_h // 2))

    dpg.configure_item('tools_window', pos=(left_pair_total + peak_info_w, 0), height=top_h)
    dpg.configure_item('plot_window', pos=(0, top_h))

    # Sliders are fixed at 150 px; centre them in the fixed-width panel
    slider_w = 150
    indent   = max(0, (peak_info_w - slider_w) // 2)
    for panel in ('pwi_top', 'pwi_bottom'):
        for child in dpg.get_item_children(panel, 1):
            if 'SliderInt' in dpg.get_item_type(child):
                dpg.configure_item(child, indent=indent)

    if _run_data is not None:
        update_tree_diagram(_run_data)


def peak_info_update(user_data):
    peak = user_data.spectrum.peaks[user_data.selected_peak]
    slider_w = 150
    panel_w = dpg.get_item_width('pwi_top')
    indent = max(0, (panel_w - slider_w) // 2) if panel_w > slider_w else 0

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
                                   width=slider_w,
                                   indent=indent,
                                   user_data=user_data,
                                   callback=update_splitting_callback)
                dpg.add_slider_int(label=f'J{ind+1}',
                                   tag=f'coupling{ind+1}',
                                   default_value=peak.couplings[ind+1],
                                   max_value=50,
                                   parent='pwi_bottom',
                                   width=slider_w,
                                   indent=indent,
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
