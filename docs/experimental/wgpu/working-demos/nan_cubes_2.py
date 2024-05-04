import pygfx as gfx
from wgpu.gui.auto import WgpuCanvas, run
import numpy as np
import time

start_time = time.time()

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

np_arr = [np.nan,np.nan,np.nan]

index_comb_list = []
positions_comb_list = []
normals_comb_list = []

cubes_x : int = 50
cubes_y : int = 50
cubes_z : int = 50

cx : int = 0
cy : int = 0
cz : int = 0

print(f"STEP 1, INITS: {time.time() - start_time} s")
start_time = time.time()

for i in range(cubes_x * cubes_y * cubes_z):
    # add new indices layer
    index_comb_temp = [[index + 25 * i for index in row] for row in index_list]
    index_comb_list.extend(index_comb_temp)
    index_comb_list.append(np_arr)

    # add new positions layer
    positions_comb_temp = [[num for num in row] for row in positions_list]
    for row in positions_comb_temp:
        row[0] += 2 * cx
        row[1] += 2 * cy
        row[2] += 2 * cz
    positions_comb_list.extend(positions_comb_temp)
    positions_comb_list.append(np_arr)
    cx += 1
    if cx == cubes_x:
        cx = 0
        cy += 1
        if(cy == cubes_y):
            cy = 0
            cz += 1

    # add new normals layer
    normals_comb_list.extend(normals_list)
    normals_comb_list.append(np_arr)

print(f"STEP 2 FOR LOOP: {time.time() - start_time} s")
start_time = time.time()

index_comb = np.array(index_comb_list, dtype=np.float32)
positions_comb = np.array(positions_comb_list, dtype=np.float32)
normals_comb = np.array(normals_comb_list, dtype=np.float32)

print(f"STEP 3, NUMPY ARRAYS: {time.time() - start_time} s")
start_time = time.time()

'''
## MULTIPROCESS FUNCTIONS
def generate_lists(i : int, cubes_x : int = 50, cubes_y : int = 50, cubes_z : int = 50, cx : int = 0, cy : int = 0, cz : int = 0):
    np_arr = [np.nan,np.nan,np.nan]
    
    index_comb_temp = [[index + 25 * i for index in row] for row in index_list]
    index_comb_temp.append(np_arr)

    # add new positions layer
    positions_comb_temp = [[num for num in row] for row in positions_list]
    for row in positions_comb_temp:
        row[0] += 2 * cx
        row[1] += 2 * cy
        row[2] += 2 * cz
    positions_comb_temp.append(np_arr)
    cx += 1
    if cx == cubes_x:
        cx = 0
        cy += 1
        if(cy == cubes_y):
            cy = 0
            cz += 1

    # add new normals layer
    normals_comb_temp = [[num for num in row] for row in positions_list]
    normals_comb_temp.append(np_arr)

    return index_comb_temp, positions_comb_temp, normals_comb_temp

def parallel_process():
    index_comb_list = []
    positions_comb_list = []
    normals_comb_list = []

    cubes_x : int = 50
    cubes_y : int = 50
    cubes_z : int = 50
    cx : int = 0
    cy : int = 0
    cz : int = 0

    with multiprocessing.Pool(processes=3) as pool:
        results = [pool.apply_async(generate_lists, (i, cubes_x, cubes_y, cubes_z, cx, cy, cz)) for i in range(cubes_x * cubes_y * cubes_z)]

        for result in results:
            index_comb_temp, positions_comb_temp, normals_comb_temp = result.get()
            index_comb_list.extend(index_comb_temp)
            positions_comb_list.extend(positions_comb_temp)
            normals_comb_list.extend(normals_comb_temp)
    return index_comb_list, positions_comb_list, normals_comb_list
'''

new_geo = gfx.Geometry(indices=index_comb, positions=positions_comb, normals=normals_comb)

cube1 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())
cube2 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())
cube3 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())
cube4 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())

cube5 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())
cube6 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())
cube7 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())
cube8 = gfx.Mesh(new_geo, gfx.MeshPhongMaterial())

cube2.world.x += 110
cube3.world.z += 110
cube4.world.z += 110
cube4.world.x += 110

cube6.world.x += 110
cube7.world.z += 110
cube8.world.z += 110
cube8.world.x += 110

cube5.world.y += 110
cube6.world.y += 110
cube7.world.y += 110
cube8.world.y += 110

#### 

canvas = WgpuCanvas(size=(640,480), title="NaN Seperate Cubes!")
renderer = gfx.WgpuRenderer(canvas)
renderer.pixel_ratio = 2
renderer._show_fps = True

camera = gfx.PerspectiveCamera(45, 16 / 9)
controller = gfx.OrbitController(camera=camera, enabled=True, register_events=renderer)

scene = gfx.Scene()
scene.add(camera)
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))
scene.add(cube1)
scene.add(cube2)
scene.add(cube3)
scene.add(cube4)

scene.add(cube5)
scene.add(cube6)
scene.add(cube7)
scene.add(cube8)

camera.show_object(scene)

print(f"STEP 4, LOADED!: {time.time() - start_time} s")
start_time = time.time()

def animate():
    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    # index_comb_list, positions_comb_list, normals_comb_list = parallel_process()
    canvas.request_draw(animate)
    run()

# print(cube.geometry.positions.data)

'''

new_indx_list2 = [[index + 25 for index in row] for row in index_list]

new_indx_comp = []
new_indx_comp += index_list
new_indx_comp += [[np.nan,np.nan,np.nan]]
new_indx_comp += new_indx_list2
new_indices_comp = np.array(new_indx_comp, dtype=np.float32)

new_pos_list2 = [[num for num in row] for row in positions_list]
for row in new_pos_list2:
    row[0] += 2

new_pos_comp = []
new_pos_comp += positions_list
new_pos_comp += [[np.nan,np.nan,np.nan]]
new_pos_comp += new_pos_list2
new_positions_comp = np.array(new_pos_comp, dtype=np.float32)

new_norm_comp = []
new_norm_comp += normals_list
new_norm_comp += [[np.nan,np.nan,np.nan]]
new_norm_comp += normals_list

new_normals_comp = np.array(new_norm_comp, dtype=np.float32)

new_indx_list2 = [
    [25, 26, 27],
    [28, 27, 26],
    [29, 30, 31],
    [32, 31, 30],
    [33, 34, 35],
    [36, 35, 34],
    [37, 38, 39],
    [40, 39, 38],
    [41, 42, 43],
    [44, 43, 42],
    [45, 46, 47],
    [48, 47, 46]
]

new_pos_list2 = [
    [ 2.5, -0.5, -0.5],
    [ 2.5,  0.5, -0.5],
    [ 2.5, -0.5,  0.5],
    [ 2.5,  0.5,  0.5],
    [ 1.5, -0.5,  0.5],
    [ 1.5,  0.5,  0.5],
    [ 1.5, -0.5, -0.5],
    [ 1.5,  0.5, -0.5],
    [ 1.5,  0.5,  0.5],
    [ 2.5,  0.5,  0.5],
    [ 1.5,  0.5, -0.5],
    [ 2.5,  0.5, -0.5],
    [ 2.5, -0.5,  0.5],
    [ 1.5, -0.5,  0.5],
    [ 2.5, -0.5, -0.5],
    [ 1.5, -0.5, -0.5],
    [ 1.5, -0.5,  0.5],
    [ 2.5, -0.5,  0.5],
    [ 1.5,  0.5,  0.5],
    [ 2.5,  0.5,  0.5],
    [ 2.5, -0.5, -0.5],
    [ 1.5, -0.5, -0.5],
    [ 2.5,  0.5, -0.5],
    [ 1.5,  0.5, -0.5], #former [-0.5,...]
]

new_indices = np.array(
    [
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
    ],
    dtype=np.float32
)
new_positions = np.array(
    [
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
    ],
    dtype=np.float32
)

new_normals = np.array(
    [
        [ 1.,  0.,  0.],
        [ 1.,  0.,  0.],
        [ 1.,  0.,  0.],
        [ 1.,  0.,  0.],
        [-1.,  0.,  0.],
        [-1.,  0.,  0.],
        [-1.,  0.,  0.],
        [-1.,  0.,  0.],
        [ 0.,  1.,  0.],
        [ 0.,  1.,  0.],
        [ 0.,  1.,  0.],
        [ 0.,  1.,  0.],
        [ 0., -1.,  0.],
        [ 0., -1.,  0.],
        [ 0., -1.,  0.],
        [ 0., -1.,  0.],
        [ 0.,  0.,  1.],
        [ 0.,  0.,  1.],
        [ 0.,  0.,  1.],
        [ 0.,  0.,  1.],
        [ 0.,  0., -1.],
        [ 0.,  0., -1.],
        [ 0.,  0., -1.],
        [ 0.,  0., -1.],
    ],
    dtype=np.float32
)

'''