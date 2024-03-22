import pygfx as gfx
from pygfx.renderers.wgpu import Binding, register_wgpu_render_function, WorldObjectShader
from pygfx.resources import Buffer

from wgpu.gui.auto import WgpuCanvas, run

import numpy as np
import pylinalg as la 
import time

class InstancedMaterial(gfx.Material):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# can you set a shader to imitate instanced mesh shader but with more customication?
@register_wgpu_render_function(gfx.WorldObject, InstancedMaterial)
class Shader(WorldObjectShader):
    type = "render"

canvas = WgpuCanvas()
renderer = gfx.WgpuRenderer(canvas)

renderer.pixel_ratio = 3

scene = gfx.Scene()

camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

# box geometry
geo = gfx.box_geometry(1.0,1.0,1.0)

cube0 = gfx.Mesh(geometry=geo, material=gfx.MeshPhongMaterial())
cube1 = gfx.Mesh(geometry=geo, material=gfx.MeshPhongMaterial())

cube0.local.x = 3

cube_grouping = gfx.Group(visible=True)

cube_grouping.add(cube0)
cube_grouping.add(cube1)

scene.add(cube_grouping)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

camera.show_object(scene)

rot = la.quat_from_euler((0, 0.01), order="XY")

def animate():
    c = np.sin(time.time())
    m = la.mat_from_translation((0, 0, 1 * c))

    cube_grouping.local.matrix = m

    cube0.local.rotation = la.quat_mul(rot, cube0.local.rotation)

    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()