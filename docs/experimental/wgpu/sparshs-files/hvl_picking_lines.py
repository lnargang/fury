import numpy as np
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
import wgpu as g

canvas = WgpuCanvas()
renderer = gfx.renderers.WgpuRenderer(canvas)
# renderer._show_fps = True
# Note that the OIT rendering for pygfx is WBOIT

# renderer.pixel_ratio = 5
scene = gfx.Scene()

num_lines = 5
pts_per_line = 3

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

mat = gfx.LineMaterial(thickness=5.0, opacity=1.)
mat.pick_write = True

line = gfx.Line(
    gfx.Geometry(positions=streamlines, colors=[(0.1, 1., 1., 0.1)]),
    mat # , color_mode='vertex'
    # for picking support : renderer.get_pick_info() or _wgpu_get_pick_info
    # Thickness + Experiments for large volume of lines
)

print(line.geometry.positions.data)

# print(g.GPUAdapter.is_fallback_adapter)

@line.add_event_handler("pointer_down")
def increase_size(event):
    info = event.pick_info
    # print(info["world_object"].geometry.positions.data)
    print(info)
    if "vertex_index" in info:
        vertex_int = info["vertex_index"]
        print("click event detected")
        # try printing current line segments locations
        print(line.geometry.positions.data[vertex_int])

        geo_pos = line.geometry.positions.data
        left_pt = vertex_int
        right_pt = vertex_int + 1
        while not np.isnan(np.min(geo_pos[left_pt])):
            left_pt -= 1
        while not np.isnan(np.min(geo_pos[right_pt])):
            right_pt += 1
        
        if left_pt < 0:
            left_pt = 0

        for pos in geo_pos:
            pos[1] += 5
        line.geometry.positions.update_range(left_pt, right_pt)

        # if line.material.thickness == 1:
        #     # print("increasing size")
        #     line.material.thickness = 10
        #     canvas.request_draw()
        # elif line.material.thickness == 10:
        #     # print("decreasing size")
        #     line.material.thickness = 1
        #     canvas.request_draw()
        canvas.request_draw()

scene.add(line)

camera = gfx.PerspectiveCamera(100, 16 / 9)
camera.local.position = (100, 100, 50)
camera.show_pos((0, 0, 0))
controller = gfx.OrbitController(camera, register_events=renderer)
# controller.add_default_event_handlers(renderer)

if __name__ == "__main__":
    canvas.request_draw(lambda: renderer.render(scene, camera))
    run()