import pygfx as gfx
from wgpu.gui.auto import WgpuCanvas, run

import numpy as np

mesh = gfx.load_mesh("C:/Users/luken/fury/docs/experimental/wgpu/jupiter.stl")
print("MODEL LOADED!")
mesh_geo = mesh[0].geometry

positions_list = mesh_geo.positions.data
indices_list = mesh_geo.indices.data
normals_list = mesh_geo.normals.data

nan_list = [np.nan, np.nan, np.nan]


indices_combined_list = []
positions_combined_list = []
normals_combined_list = []

cubes_x : int = 2
cubes_y : int = 2
cubes_z : int = 2

cx : int = 0
cy : int = 0
cz : int = 0

model_indices = {}
current_model_index : int = 0
current_model_positions_index_lower : int = 0

for i in range(cubes_x * cubes_y * cubes_z):
    indices_comb_temp = [[index + 363996 * i for index in row] for row in indices_list]

    indices_combined_list.extend(indices_comb_temp)
    indices_combined_list.append(nan_list)

    model_indices[current_model_index] = [current_model_positions_index_lower, current_model_positions_index_lower + 363995]
    current_model_index += 1
    current_model_positions_index_lower += 363996

    positions_comb_temp = [[num for num in row] for row in positions_list]
    for row in positions_comb_temp:
        row[0] += 340 * cx
        row[1] += 340 * cy
        row[2] += 340 * cz

    cx += 1
    if cx == cubes_x:
        cx = 0
        cy += 1
        if(cy == cubes_y):
            cy = 0
            cz += 1

    positions_combined_list.extend(positions_comb_temp)
    positions_combined_list.append(nan_list)

    normals_combined_list.extend(normals_list)
    normals_combined_list.append(nan_list)


index_array = np.array(indices_combined_list, dtype=np.float32)
positions_array = np.array(positions_combined_list, dtype=np.float32)
normals_array = np.array(normals_combined_list, dtype=np.float32)

comb_geo = gfx.Geometry(indices=index_array, positions=positions_array, normals=normals_array)
mat = gfx.MeshPhongMaterial()
mat.pick_write = True
mesh = gfx.Mesh(comb_geo, mat)

canvas = WgpuCanvas(size=(640, 480), title="MODEL LOADING")
rend = gfx.WgpuRenderer(canvas)
rend.pixel_ratio = 2
camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=rend)
scene = gfx.Scene()
scene.add(camera)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))
scene.add(mesh)
camera.show_object(scene)
camera.depth_range = 0.01, 10000

def on_click(event):
    info = event.pick_info
    # print(info)
    if "face_index" in info:
        face_index = info["face_index"]

        indices_range = model_indices[int(face_index / (len(indices_list) + 1))]
        left_index = indices_range[0]
        right_index = indices_range[1]

        # sub_index = np.argmax(info["face_coord"])
        # vertex_index = int(event.target.geometry.indices.data[face_index, sub_index])
        # left_index = vertex_index
        # while not np.isnan(np.min(event.target.geometry.positions.data[left_index - 1])):
        #     left_index -= 1
        # right_index = left_index + 8706
              
        pos = event.target.geometry.positions.data[left_index : right_index]
        for row in pos:
            row[1] += 40

        # print(f"SELECTED FACE INDEX {face_index} WHICH IS CUBE {index_lookup_list[face_index]} WITH POSITIONS VALUES RANGING {model_indices[index_lookup_list[face_index]]}")
        event.target.geometry.positions.update_range(left_index, right_index)

mesh.add_event_handler(on_click, "pointer_down")

def animate():
    rend.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()
