import pygfx as gfx
import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import pylinalg as la
import numpy as np

import time

canvas = WgpuCanvas(size=(640,480))
renderer = gfx.WgpuRenderer(canvas)
scene = gfx.Scene()

geometry = gfx.box_geometry(1.0,1.0,1.0)

x_max = 900
y_max = 100

instanced_mesh = gfx.InstancedMesh(geometry, gfx.MeshPhongMaterial(), x_max * y_max)

# print(instanced_mesh.geometry)

for y in range(y_max):
    for x in range(x_max):
        m = la.mat_from_translation((y * 2, x * 2, 0))
        instanced_mesh.set_matrix_at(x + y * x_max, m)

        # add rotation


scene.add(instanced_mesh)

def on_pick(event):
    info = event.pick_info
    print(info)

    # info['world_object']
    # scene.remove(instanced_mesh)

    # m = la.mat_from_translation((1, 1, 4))
    # instanced_mesh.set_matrix_at(info["instance_index"], m)

     # scene.add(instanced_mesh)
    

instanced_mesh.add_event_handler(on_pick, "pointer_down")

camera = gfx.PerspectiveCamera(45, 16 / 9)
camera.show_object(scene)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

camera.depth_range = 0.01, 100000

scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

def animate():
    start_time = time.time()
    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

    rot = la.quat_from_euler((0,0.01), order="xy")
    # rotation = la.quat_mul(rot, instanced_mesh.children[0].local.rotation)
    # instanced_mesh.
    # print(instanced_mesh.children)
    

    # instanced_mesh.children[0].local.rotation = rotation

    print(f'FPS: {1 / (time.time() - start_time)}')

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()