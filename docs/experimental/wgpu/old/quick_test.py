import pygfx as gfx
from pygfx.renderers.wgpu import Binding, register_wgpu_render_function, WorldObjectShader
from pygfx.resources import Buffer

from wgpu.gui.auto import WgpuCanvas, run

import numpy as np
import pylinalg as la 
import time

canvas = WgpuCanvas()
renderer = gfx.WgpuRenderer(canvas)

renderer.pixel_ratio = 3

scene = gfx.Scene()

camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

# box geometry
geo = gfx.box_geometry(1.0,1.0,1.0)
rot = la.quat_from_euler((0, 0.01), order="XY")

cubes = [gfx.Mesh(geo, gfx.MeshBasicMaterial()) for i in range(5000)]

cube1 = gfx.Mesh(geo, gfx.MeshBasicMaterial())
cube1.local.position = (-2, -2, -2)

x = 0
y = 0

cube_grouping = gfx.Group(visible=False)
for i, cube in enumerate(cubes):
    cube.local.position = (x * 2, y * 2, 0)
    cube_grouping.add(cube)
    x += 1
    if x >= 50:
        x = 0
        y += 1

scene.add(cube_grouping)
scene.add(cube1)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

camera.show_object(scene)

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