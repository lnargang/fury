import pygfx as gfx
from wgpu.gui.auto import WgpuCanvas, run

import numpy as np
import copy

import pylinalg as la

index_list = [
    [0, 1, 2],
    [3, 2, 1],
    [4, 5, 6],
    [7, 6, 5],
    [8, 9, 10],
    [11, 10, 9],
    [12, 13, 14],
    [15, 14, 13],
    [16, 17, 18],
    [19, 18, 17],
    [20, 21, 22],
    [23, 22, 21]
]

positions_list = [
    [ 0.5, -0.5, -0.5],
    [ 0.5,  0.5, -0.5],
    [ 0.5, -0.5,  0.5],
    [ 0.5,  0.5,  0.5],
    [-0.5, -0.5,  0.5],
    [-0.5,  0.5,  0.5],
    [-0.5, -0.5, -0.5],
    [-0.5,  0.5, -0.5],
    [-0.5,  0.5,  0.5],
    [ 0.5,  0.5,  0.5],
    [-0.5,  0.5, -0.5],
    [ 0.5,  0.5, -0.5],
    [ 0.5, -0.5,  0.5],
    [-0.5, -0.5,  0.5],
    [ 0.5, -0.5, -0.5],
    [-0.5, -0.5, -0.5],
    [-0.5, -0.5,  0.5],
    [ 0.5, -0.5,  0.5],
    [-0.5,  0.5,  0.5],
    [ 0.5,  0.5,  0.5],
    [ 0.5, -0.5, -0.5],
    [-0.5, -0.5, -0.5],
    [ 0.5,  0.5, -0.5],
    [-0.5,  0.5,-0.5],
]

normals_list = [
    [ 1,  0,  0],
    [ 1,  0,  0],
    [ 1,  0,  0],
    [ 1,  0,  0],
    [-1,  0,  0],
    [-1,  0,  0],
    [-1,  0,  0],
    [-1,  0,  0],
    [ 0,  1,  0],
    [ 0,  1,  0],
    [ 0,  1,  0],
    [ 0,  1,  0],
    [ 0, -1,  0],
    [ 0, -1,  0],
    [ 0, -1,  0],
    [ 0, -1,  0],
    [ 0,  0,  1],
    [ 0,  0,  1],
    [ 0,  0,  1],
    [ 0,  0,  1],
    [ 0,  0, -1],
    [ 0,  0, -1],
    [ 0,  0, -1],
    [ 0,  0, -1],
]

nan_list = [np.nan,np.nan,np.nan]

index_combined_list = []
positions_combined_list = []
normals_combined_list = []

cubes_x : int = 1
cubes_y : int = 1
cubes_z : int = 4

cx : int = 0
cy : int = 0
cz : int = 0

# index_lookup_list = []
cube_indices = {}
current_cube_index : int = 0
current_cube_lower_index : int = 0

cube_angles = []

for i in range(cubes_x * cubes_y * cubes_z):
    # add new indices layer
    index_comb_temp = [[index + 25 * i for index in row] for row in index_list]
    index_combined_list.extend(index_comb_temp)
    index_combined_list.append(nan_list)

    cube_indices[current_cube_index] = [current_cube_lower_index, current_cube_lower_index + 24]
    current_cube_index += 1
    current_cube_lower_index += 25

    # add new positions layer
    positions_comb_temp = [[num for num in row] for row in positions_list]
    for row in positions_comb_temp:
        row[0] += 2 * cx
        row[1] += 2 * cy
        row[2] += 2 * cz
    positions_combined_list.extend(positions_comb_temp)
    positions_combined_list.append(nan_list)
    cx += 1
    if cx == cubes_x:
        cx = 0
        cy += 1
        if(cy == cubes_y):
            cy = 0
            cz += 1

    # add new normals layer
    normals_combined_list.extend(normals_list)
    normals_combined_list.append(nan_list)

    cube_angles.append(0)

index_array = np.array(index_combined_list, dtype=np.float32)
positions_array = np.array(positions_combined_list, dtype=np.float32)
normals_array = np.array(normals_combined_list, dtype=np.float32)

cubes_geometry = gfx.Geometry(indices=index_array, positions=positions_array, normals=normals_array)

pickable_mat = gfx.MeshPhongMaterial()
pickable_mat.pick_write = True
mesh = gfx.Mesh(cubes_geometry, pickable_mat)

# SCENE SETUP
canvas = WgpuCanvas(size=(640,480), title="Pickable NaN Cubes!")
renderer = gfx.WgpuRenderer(canvas)
renderer.blend_mode = "weighted_plus"
renderer.pixel_ratio = 2
renderer._show_fps = False
camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)
scene = gfx.Scene()
scene.add(camera)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

scene.add(mesh)

camera.show_object(scene)
camera.depth_range = 0.01, 10000

def rotate_cubes(mesh : gfx.Mesh):
    for index in cube_indices:
        indices_range = cube_indices[index]

        left_index = indices_range[0]
        right_index = indices_range[1]

        pos = mesh.geometry.positions.data[left_index : right_index]
        norms = mesh.geometry.normals.data[left_index : right_index]
        _angle = 0
        if index == 0:
            _angle = 1
        if index == 1:
            _angle = 2
        if index == 2:
            _angle = 3
        if index == 3:
            _angle = 4

        for row in pos:
            x_2 = ((row[1]) * np.cos(np.deg2rad(_angle))) - ((row[2]) * np.sin(np.deg2rad(_angle)))
            y_2 = ((row[1]) * np.sin(np.deg2rad(_angle))) + ((row[2]) * np.cos(np.deg2rad(_angle)))
            row[1] = x_2
            row[2] = y_2
        ## NORMALS NOT BEING CORRECTED PROPERLY
        for row in norms:
            x_2 = ((row[1]) * np.cos(np.deg2rad(_angle))) - ((row[2]) * np.sin(np.deg2rad(_angle)))
            y_2 = ((row[1]) * np.sin(np.deg2rad(_angle))) + ((row[2]) * np.cos(np.deg2rad(_angle)))
            row[1] = x_2
            row[2] = y_2

        mesh.geometry.positions.update_range(left_index, right_index)
        mesh.geometry.normals.update_range(left_index, right_index)
    pass

def animate():
    rotate_cubes(mesh=mesh)
    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()