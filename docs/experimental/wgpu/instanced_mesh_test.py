#TODO: build the data for a box

# Distinction between shader and geometry data. Further stress test instancing, and throw a shader onto the cube
# Figure out if instancing or geometry repetition is better

# check geometries/_base to figure out if geometry is manually define-able

# how to develop per EG:
# first create a very simple streamline (mesh in my case)
# defines the points 

# is there any way with one call to render many things -> double check instancing
# understand how they are putting everything on the shder

import numpy as np

streamline = np.array([[0,0,0.], [5,0,0], [10,10,0.]], dtype='f4')

# define the connections between the points
connectivity = [[0,1,2]]


import pygfx as gfx
import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import pylinalg as la

import pygfx.geometries.utils as pyutils

canvas = WgpuCanvas(size=(1280,720))
renderer = gfx.WgpuRenderer(canvas)
scene = gfx.Scene()

# does geometry merging work??
# difficult to access geometries/utils.py -> maybe try to reimplement?

geo = gfx.box_geometry(1.0,1.0,1.0)

# mesh_temp2.local.x = 3.0

mesh_temp3_instanced = gfx.InstancedMesh(geo, gfx.MeshPhongMaterial(), 10000)

for y in range(100):
    for x in range(100):
        m = la.mat_from_translation((y * 2, x * 2, 0))
        mesh_temp3_instanced.set_matrix_at(x + y * 99, m)
# scene.add(mesh_temp1, mesh_temp2)

# scene.add(mesh_temp3_instanced)

mesh_temp2_instanced = gfx.InstancedMesh(geo, gfx.MeshPhongMaterial(), 100)

for y in range(10):
    for x in range(10):
        m = la.mat_from_translation((y * 2, x * 2, 0))
        mesh_temp2_instanced.set_matrix_at(x + y * 10, m)

# scene.add(mesh_temp3_instanced)
# scene.add(mesh_temp2_instanced)

# scene display
        
for y in range(50):
    for x in range(100):
        mesh_temp4 = gfx.Mesh(geo, gfx.MeshPhongMaterial())
        mesh_temp4.local.x = x * 2
        mesh_temp4.local.y = y * 2
        # scene.add(mesh_temp4)

camera = gfx.PerspectiveCamera(45, 16 / 9)
camera.show_object(scene)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

line = gfx.Line(
    gfx.Geometry(positions=streamline, indices=connectivity),
    gfx.LineMaterial(thickness=1.0)
)
scene.add(line)

def animate():
    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()