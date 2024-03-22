# 
'''
import pygfx as gfx
import pylinalg as la

import numpy as np
import time

geo = gfx.box_geometry(1.0,1.0,1.0)

instanced_mesh = gfx.InstancedMesh(
    geometry=geo, material=gfx.MeshPhongMaterial(), count=25
)

temp_cube = gfx.Mesh(
    geometry=geo,
    material=gfx.MeshPhongMaterial()
)

for y in range(5):
    for x in range(5):
        m = la.mat_from_translation((x * 2, y * 2, 0))
        instanced_mesh.set_matrix_at(x + y*5, m)

rot = la.quat_from_euler((0,0.01), order="XY")

def animate():
    # temp_cube.local.rotation = la.quat_mul(rot, temp_cube.local.rotation)
    # print(np.sin(time.time()))
    c = np.sin(time.time())
    m = la.mat_from_translation((0, 0, 4 * c))
    instanced_mesh.set_matrix_at(0, m)

    instanced_mesh.local.matrix = m

    # instanced_mesh._update_uniform_buffers()

    temp_cube.local.matrix = m

    # instanced_mesh.set_matrix_at(0,temp_cube.local.matrix)


if __name__ == "__main__":
    gfx.show(temp_cube, before_render=animate)
    gfx.show(instanced_mesh, before_render=animate)



'''
import pygfx as gfx
import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import pylinalg as la
import numpy as np

import time

canvas = WgpuCanvas(size=(640,480))
renderer = gfx.WgpuRenderer(canvas)
renderer.pixel_ratio = 2
scene = gfx.Scene()

geometry = gfx.box_geometry(1.0,1.0,1.0)

x_max = 750
y_max = 750

time_start = time.time()
instanced_mesh = gfx.InstancedMesh(geometry, gfx.MeshPhongMaterial(), x_max * y_max)

print(f"TIME TO GENERATE instanced mesh (s): {time.time() - time_start}")
time_start = time.time()

for y in range(y_max):
    for x in range(x_max):
        m = la.mat_from_translation((y * 2, x * 2, 0))
        instanced_mesh.set_matrix_at(x + y * x_max, m)

print(f"TIME TO UPDATE instanced mesh (s): {time.time() - time_start}")
time_start = time.time()

scene.add(instanced_mesh)


def on_pick(event):
    info = event.pick_info
    print(info)

    # info['world_object']
    
instanced_mesh.add_event_handler(on_pick, "pointer_down")

camera = gfx.PerspectiveCamera(45, 16 / 9)
camera.show_object(scene)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

camera.depth_range = 0.01, 100000

scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

print(f"TIME TO add to scene (s): {time.time() - time_start}")
time_start = time.time()

def animate():
    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()

#