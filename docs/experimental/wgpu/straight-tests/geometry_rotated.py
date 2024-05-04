import pygfx as gfx
from wgpu.gui.auto import WgpuCanvas, run
import pylinalg as la

import time
import numpy as np

import pybullet as pyb
import pybullet_data
import pyb_utils

# GPU-Based phyics in future impl

import pygfx as gfx
import wgpu
enums_gpu = wgpu.gpu.enumerate_adapters()
gfx.renderers.wgpu.select_power_preference("high-performance")
gfx.renderers.wgpu.select_adapter(enums_gpu[0])

# PYGFX
canvas = WgpuCanvas(max_fps=120)
renderer = gfx.WgpuRenderer(canvas)
renderer.pixel_ratio = 2
# renderer._show_fps = True
camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer, damping=1)
scene = gfx.Scene()
camera.depth_range = 0.01, 10000
scene.add(camera)
# light = gfx.DirectionalLight()
# light.cast_shadow = True
scene.add(gfx.AmbientLight("#111111"))
# scene.add(camera.add(light))

# PY BULLET SETUP
pyb.connect(pyb.DIRECT)
pyb.setGravity(0, -200, 0)
pyb.setTimeStep(1. / 240.)
pyb.setAdditionalSearchPath(pybullet_data.getDataPath())

## ADD CUBES
cubes_list = []
box_list = []

boxes_x : int = 5
boxes_y : int = 5
for y in range(boxes_x):
    for x in range(boxes_y):
        cube = gfx.Mesh(gfx.box_geometry(1,1,1), gfx.MeshPhongMaterial())
        box = pyb_utils.BulletBody.box([0.4 * y,y * 1, (x - (boxes_x / 2.)) * 1], half_extents=[0.5, 0.5, 0.5], mass = 2)

        cube.local.position, cube.local.rotation = box.get_pose()
        cube.cast_shadow = True
        cube.receive_shadow = True

        scene.add(cube)
        cubes_list.append(cube)
        box_list.append(box)

cube_1 = gfx.Mesh(gfx.box_geometry(10, 0.3, 10), gfx.MeshPhongMaterial(color=(1.0, 0.0, 0.0)))
box_1 = pyb_utils.BulletBody.box([0, -3, 0], half_extents=[5, 0.15, 5], mass=0)
cube_1.local.position, cube_1.local.rotation = box_1.get_pose()
cube_1.receive_shadow = True
scene.add(cube_1)

cube_2 = gfx.Mesh(gfx.box_geometry(1.2, 1.2, 1.2), gfx.MeshPhongMaterial(color=(0.0, 0.0, 1.0)))
box_2 = pyb_utils.BulletBody.box([0, -1.5, 0], half_extents=[0.5, 0.5, 0.5], mass=1)
cube_2.local.position, cube_2.local.rotation = box_2.get_pose()
scene.add(cube_2)
cube_2.receive_shadow = True


spot_light = gfx.SpotLight("#ffffff", 250, angle=0.4, penumbra=0.3, decay=2)
spot_light.cast_shadow = True
spot_light.local.position = (-5, 10, 5)
# spot_light.add(gfx.SpotLightHelper())
scene.add(spot_light)

def animate():
    indices_to_remove = []
    for i in range(len(box_list)):
        cubes_list[i].local.position, cubes_list[i].local.rotation = box_list[i].get_pose()

        if cubes_list[i].local.y < -15:
            indices_to_remove.append(i)

    for i in indices_to_remove:
        scene.remove(cubes_list[i])
        box_list.pop(i)
        cubes_list.pop(i)
    # box_1.set_velocity(angular=[0,5,0, 1.0])
    # cube_1.local.position, cube_1.local.rotation = box_1.get_pose()
    cube_2.local.position, cube_2.local.rotation = box_2.get_pose()
    
    time.sleep(1. / 240.)
    # box1.set_velocity(linear=[0,0,0], angular=[0,0,0,1.])
    pyb.stepSimulation()

    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

    # print(cube_1.world.rotation)
    # camera_position_vector = list(camera.world.position)
    # print(la.vec_normalize(camera_position_vector))

    # vec = la.vec_normalize(camera_position_vector)
    # pyb.setGravity(vec[0], vec[2], vec[1])

camera.show_object(scene)
if __name__ == "__main__":
    canvas.request_draw(animate)
    run()