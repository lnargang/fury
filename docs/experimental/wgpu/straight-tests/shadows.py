import time
import math
import random
import pylinalg as la

from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx

renderer = gfx.renderers.WgpuRenderer(WgpuCanvas(max_fps=60))

scene = gfx.Scene()
camera = gfx.PerspectiveCamera(35, 16 / 9)
camera.local.position = (46, 22, -21)
camera.show_pos((0, 7, 0))

gfx.OrbitController(camera, register_events=renderer)

floor = gfx.Mesh(
    gfx.plane_geometry(2000, 2000),
    gfx.MeshPhongMaterial(color="#808080", side="Front"),
)

floor.local.rotation = la.quat_from_euler(-math.pi / 2, order="X")
floor.local.position = (0, -0.05, 0)
floor.receive_shadow = True

box = gfx.Mesh(
    gfx.box_geometry(3, 1, 2),
    gfx.MeshPhongMaterial(color="#aaaaaa"),
)

box.cast_shadow = True
box.receive_shadow = True
box.local.position = (0, 5, 0)

ambient = gfx.AmbientLight("#111111")

light = gfx.SpotLight("#ff7f00", 2000, angle=0.3, penumbra=0.2, decay=2)
light.cast_shadow = True

light.local.position = (15, 40, 45)

light.add(gfx.SpotLightHelper())
scene.add(box)
scene.add(floor)
scene.add(ambient)
scene.add(light)

def animate():
    renderer.render(scene, camera)
    renderer.request_draw()
    pass


if __name__ == "__main__":
    renderer.request_draw(animate)
    run()