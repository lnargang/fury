import numpy as np
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
import wgpu as g

canvas = WgpuCanvas()
renderer = gfx.renderers.WgpuRenderer(canvas)
renderer._show_fps = True
# Note that the OIT rendering for pygfx is WBOIT

# renderer.pixel_ratio = 5
scene = gfx.Scene()

num_lines = 10
pts_per_line = 20

start_points = np.random.uniform(-10, 10, size=(num_lines, 3))

points_per_line = []
for i in range(num_lines):
    origin = start_points[i]
    x = np.linspace(0, 10 * pts_per_line, pts_per_line)
    y = np.sin(x) + origin[0]
    z = np.cos(x) + origin[1]
    points_per_line.append(np.column_stack((x, y, z)))

streamlines = np.zeros((num_lines * (pts_per_line + 1), 3), dtype=np.float32)

for i in range(num_lines):
    start_idx = i * (pts_per_line + 1)
    end_idx = start_idx + pts_per_line
    streamlines[start_idx:end_idx] = points_per_line[i]
    streamlines[end_idx] = [np.nan, np.nan, np.nan]

line = gfx.Line(
    gfx.Geometry(positions=streamlines, colors=[(0.1, 1., 1., 0.1)]),
    gfx.LineMaterial(thickness=1.0, opacity=1.) # , color_mode='vertex'
    # for picking support : renderer.get_pick_info() or _wgpu_get_pick_info
    # Thickness + Experiments for large volume of lines
)

print(line.geometry.positions.data)