import numpy as np
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
import wgpu as g

canvas = WgpuCanvas()
renderer = gfx.renderers.WgpuRenderer(canvas, show_fps=True)
# renderer.pixel_ratio = 5
scene = gfx.Scene()
# renderer._show_fps = True
# streamline = np.array([[0,0,0], [0,2,2], [np.nan, np.nan, np.nan], [0, 2, 4], [4, 4, 4], [6, 10, 6], [6, 10, 7]], dtype=np.float32)
# connect = np.array([0, 1, 2]) # indices not working currently

num_lines = 1_000
pts_per_line = 5

points_per_line = np.random.uniform(0, 10, size=(num_lines, pts_per_line, 3))

streamlines = np.zeros((num_lines * (pts_per_line + 1), 3), dtype=np.float32)

for i in range(num_lines):
    start_idx = i * (pts_per_line + 1)
    end_idx = start_idx + pts_per_line
    streamlines[start_idx:end_idx] = points_per_line[i]
    # nan buffering the lines
    streamlines[end_idx] = np.asarray([np.nan, np.nan, np.nan])

line = gfx.Line(
    # gfx.positions.data will return our np array given
    gfx.Geometry(positions=streamlines, colors=[(0, 1., 1., 1.)]),
    gfx.LineMaterial(thickness=1.0, opacity=0.5) # , color_mode='vertex'
    # for picking support : renderer.get_pick_info() or _wgpu_get_pick_info
)

#print(line.geometry.positions.data)

# print(g.GPUAdapter.is_fallback_adapter)


@line.add_event_handler("pointer_down")
def increase_size(event):
    info = event.pick_info
    print(info)
    if "vertex_index" in info:
        print("click event detected")
        # try printing current line segments locations
        if line.material.thickness == 1:
            # print("increasing size")
            line.material.thickness = 10
            canvas.request_draw()
        elif line.material.thickness == 10:
            # print("decreasing size")
            line.material.thickness = 1
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