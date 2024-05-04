import numpy as np
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
import wgpu as g

canvas = WgpuCanvas()
renderer = gfx.renderers.WgpuRenderer(canvas)
# renderer.pixel_ratio = 5
scene = gfx.Scene()

num_lines = 1_000
pts_per_line = 100

start_points = np.random.uniform(-100, 100, size=(num_lines, 3))

points_per_line = []
for i in range(num_lines):

    origin = start_points[i]
    x = np.linspace(0, 10 * pts_per_line, pts_per_line)

    phase_sin = np.random.uniform(0, 2*np.pi)
    phase_cos = np.random.uniform(0, 2*np.pi)
    y = np.sin(x + phase_sin) + origin[0]
    z = np.cos(x + phase_cos) + origin[1]

    rotation_x = np.random.uniform(0, 2*np.pi)
    rotation_y = np.random.uniform(0, 2*np.pi)
    rotation_z = np.random.uniform(0, 2*np.pi)
    
    rotated_y = y * np.cos(rotation_x) - z * np.sin(rotation_x)
    rotated_z = y * np.sin(rotation_x) + z * np.cos(rotation_x)
    y = rotated_y
    z = rotated_z
    
    rotated_x = x * np.cos(rotation_y) - z * np.sin(rotation_y)
    rotated_z = x * np.sin(rotation_y) + z * np.cos(rotation_y)
    x = rotated_x
    z = rotated_z
    
    rotated_x = x * np.cos(rotation_z) - y * np.sin(rotation_z)
    rotated_y = x * np.sin(rotation_z) + y * np.cos(rotation_z)
    x = rotated_x
    y = rotated_y

    points_per_line.append(np.column_stack((x, y, z)))

streamlines = np.zeros((num_lines * (pts_per_line + 1), 3), dtype=np.float32)

for i in range(num_lines):
    start_idx = i * (pts_per_line + 1)
    end_idx = start_idx + pts_per_line
    streamlines[start_idx:end_idx] = points_per_line[i]
    streamlines[end_idx] = [np.nan, np.nan, np.nan]

line = gfx.Line(
    gfx.Geometry(positions=streamlines, colors=[(0.1, 1., 1., 0.1)]),
    gfx.LineMaterial(thickness=1.0, opacity=0.6) # , color_mode='vertex'
    # for picking support : renderer.get_pick_info() or _wgpu_get_pick_info
    # Thickness + Experiments for large volume of lines
)

print(line.geometry.positions.data)

# print(g.GPUAdapter.is_fallback_adapter)
def pick():
    info = renderer.get_pick_info()

scene.add(line)

camera = gfx.PerspectiveCamera(100, 16 / 9)
camera.local.position = (100, 100, 50)
camera.show_pos((0, 0, 0))
controller = gfx.OrbitController(camera, register_events=renderer)
# controller.add_default_event_handlers(renderer)

if __name__ == "__main__":
    canvas.request_draw(lambda: renderer.render(scene, camera))
    run()