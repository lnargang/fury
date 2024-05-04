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

cubes_x : int = 3
cubes_y : int = 3
cubes_z : int = 2

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
    '''
    for row in index_list:
        index_lookup_list.append(current_cube_index)
    index_lookup_list.append(current_cube_index)
    '''
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

# other mesh
cubes_geometry_2 = gfx.Geometry(indices=index_array, positions=copy.deepcopy(positions_array), normals=normals_array)
## TO MAKE ANOTHER MESH WITH *DISTINCT* GEOMETRY, WE ONLY NEED TO DEEP COPY THE POSITIONS ARRAY. ALL OTHER DATA REMAINS CONSTANT AND CAN BE REUSED.
mesh_2 = gfx.Mesh(cubes_geometry_2, pickable_mat)
mesh_2.world.z += 3 * cubes_y

# SCENE SETUP
canvas = WgpuCanvas(size=(640,480), max_fps=60, title="Pickable NaN Cubes!")
renderer = gfx.WgpuRenderer(canvas)
renderer.blend_mode = "weighted_plus"
renderer.pixel_ratio = 2
camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)
scene = gfx.Scene()
scene.add(camera)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

scene.add(mesh_2)

camera.show_object(scene)
camera.depth_range = 0.01, 10000

# PICKING INFORMATION

def on_click(event):
    global cube_angles
    info = event.pick_info

    if "face_index" in info:
        face_index = info["face_index"]
        face_coord = info["face_coord"]

        ## GET INDEX OF ORIGINAL POSITION
        cube_index = int(face_index / (len(index_list) + 1))
        indices_range = cube_indices[cube_index]
        left_index = indices_range[0]
        right_index = indices_range[1]

        pos = event.target.geometry.positions.data[left_index : right_index]
        norms = event.target.geometry.normals.data[left_index : right_index]

        sub_pos_array = positions_array[left_index : right_index]
        cube_angles[cube_index] += 45
        _angle = cube_angles[cube_index]

        og_index = 0
        for row in pos:
            og_l = positions_list[og_index]
            offset = sub_pos_array[og_index] - og_l
            og_index += 1

            x_2 = ((og_l[1]) * np.cos(np.deg2rad(_angle))) - ((og_l[2]) * np.sin(np.deg2rad(_angle)))
            y_2 = ((og_l[1]) * np.sin(np.deg2rad(_angle))) + ((og_l[2]) * np.cos(np.deg2rad(_angle)))
            row[1] = x_2 + offset[1]
            row[2] = y_2 + offset[2]
            # GPU/Matrix Rotations - correction towards shader in order to add transformations on the GPU-level
            # shaders - next step
            # boids - follow path and flocking? old fury used rotations on CPU and not on shader so it results in
            # stutter, slow down. etc.
            # SEE BOIDS PR ON FURY PROJECT GIT - rotation matrices shader etc.

            # need to come up with a transformation matrix implementation on shader (difficult is doing it per-cube on a larger object)
            # can provide a vector and allow things to be realligned
            # shader will update internally, not externally like current IMPL
            # extend mesh shader specifically
            # update vertex more specifically

            # start getting used to passing variables and arrays between GPU, webGL
        og_index = 0
        for row in norms:
            og_n = normals_list[og_index]
            og_index += 1
            x_2 = ((og_n[1]) * np.cos(np.deg2rad(_angle))) - ((og_n[2]) * np.sin(np.deg2rad(_angle)))
            y_2 = ((og_n[1]) * np.sin(np.deg2rad(_angle))) + ((og_n[2]) * np.cos(np.deg2rad(_angle)))
            row[1] = x_2
            row[2] = y_2

        event.target.geometry.positions.update_range(left_index, right_index)
        event.target.geometry.normals.update_range(left_index, right_index)

mesh_2.add_event_handler(on_click, "pointer_down")

# rot = la.quat_from_euler((0,0.01), order="XY")

def rotate_all(mesh : gfx.Mesh):
    global cube_angles

    for index in cube_indices:
        ## GET INDEX OF ORIGINAL POSITION
        indices_range = cube_indices[index]
        left_index = indices_range[0]
        right_index = indices_range[1]

        pos = mesh.geometry.positions.data[left_index : right_index]
        norms = mesh.geometry.normals.data[left_index : right_index]

        sub_pos_array = positions_array[left_index : right_index]
        cube_angles[index] += 1
        _angle = cube_angles[index]

        og_index = 0
        for row in pos:
            og_l = positions_list[og_index]
            offset = sub_pos_array[og_index] - og_l
            og_index += 1

            x_2 = ((og_l[1]) * np.cos(np.deg2rad(_angle))) - ((og_l[2]) * np.sin(np.deg2rad(_angle)))
            y_2 = ((og_l[1]) * np.sin(np.deg2rad(_angle))) + ((og_l[2]) * np.cos(np.deg2rad(_angle)))
            row[1] = x_2 + offset[1]
            row[2] = y_2 + offset[2]
        ## NORMALS NOT BEING CORRECTED PROPERLY
        og_index = 0
        for row in norms:
            og_n = normals_list[og_index]
            og_index += 1
            x_2 = ((og_n[1]) * np.cos(np.deg2rad(_angle))) - ((og_n[2]) * np.sin(np.deg2rad(_angle)))
            y_2 = ((og_n[1]) * np.sin(np.deg2rad(_angle))) + ((og_n[2]) * np.cos(np.deg2rad(_angle)))
            row[1] = x_2
            row[2] = y_2

        mesh.geometry.positions.update_range(left_index, right_index)
        mesh.geometry.normals.update_range(left_index, right_index)

def animate():
    rotate_all(mesh=mesh_2)
    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()