import pygfx as gfx
from pygfx.renderers.wgpu import Binding, register_wgpu_render_function, WorldObjectShader
from pygfx.resources import Buffer

from wgpu.gui.auto import WgpuCanvas, run

import numpy as np
import pylinalg as la 
import time

canvas = WgpuCanvas()
renderer = gfx.WgpuRenderer(canvas)
renderer.pixel_ratio = 2

renderer.pixel_ratio = 3

scene = gfx.Scene()

camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

# box geometry
geo = gfx.box_geometry(1.0,1.0,1.0)

rot = la.quat_from_euler((0, 0.01), order="XY")

def on_pick(event):
    info = event.pick_info

time_start = time.time()
cubes = [gfx.Mesh(geo, gfx.MeshBasicMaterial()) for i in range(100)]

print(f"TIME TO GENERATE cubes ARRAY (s): {time.time() - time_start}")
time_start = time.time()
x = 0
y = 0

groupings = []

for i in range(100):
    cube_grouping = gfx.Group(visible=True)
    for i, cube in enumerate(cubes):
        cube.local.position = (x * 2, y * 2, 0)
        # cube.add_event_handler(on_pick, "pointer_down")
        cube_grouping.add(cube)
        x += 1
        if x >= 100:
            x = 0
            y += 1
    groupings.append(cube_grouping)

print(f"TIME TO GENERATE cube_groupings (s): {time.time() - time_start}")
time_start = time.time()

group_grouping = gfx.Group(visible=True)

x = 0
y = 0
for group2 in groupings:
    # print("ADDED GROUP")
    group2.local.position = (x * 200, y * 200, 0)
    group_grouping.add(group2)
    x += 1
    if x >= 10:
        x + 0
        y += 1

print(f"TIME TO GENERATE group_groupings (s): {time.time() - time_start}")
time_start = time.time()

scene.add(cube_grouping)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

camera.show_object(scene)

print(f"TIME TO load scene (s): {time.time() - time_start}")
time_start = time.time()

def animate():
    c = np.sin(time.time())
    m = la.mat_from_translation((0, 0, 1 * c))

    # cube_grouping.local.matrix = m

    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()

# before;
