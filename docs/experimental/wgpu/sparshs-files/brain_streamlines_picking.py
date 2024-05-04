from dipy.core.gradients import gradient_table
from dipy.data import get_fnames, default_sphere
from dipy.direction import peaks_from_model
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti, load_nifti_data
from dipy.reconst.csdeconv import auto_response_ssst
from dipy.reconst.shm import CsaOdfModel
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion
from dipy.tracking import utils
from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.streamline import Streamlines

hardi_fname, hardi_bval_fname, hardi_bvec_fname = get_fnames('stanford_hardi')
label_fname = get_fnames('stanford_labels')
data, affine, hardi_img = load_nifti(hardi_fname, return_img=True)
labels = load_nifti_data(label_fname)
bvals, bvecs = read_bvals_bvecs(hardi_bval_fname, hardi_bvec_fname)
gtab = gradient_table(bvals, bvecs)
white_matter = (labels == 1) | (labels == 2)
response, ratio = auto_response_ssst(gtab, data, roi_radii=10, fa_thr=0.7)
csa_model = CsaOdfModel(gtab, sh_order_max=6)
csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                             relative_peak_threshold=.8,
                             min_separation_angle=45,
                             mask=white_matter)
stopping_criterion = ThresholdStoppingCriterion(csa_peaks.gfa, .25)

sli = csa_peaks.gfa.shape[2] // 2
seed_mask = (labels == 2)
seeds = utils.seeds_from_mask(seed_mask, affine, density=[2, 2, 2])
streamlines_generator = LocalTracking(csa_peaks, stopping_criterion, seeds,
                                      affine=affine, step_size=.5)
streamlines = Streamlines(streamlines_generator)

# Pygfx
import numpy as np
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx

canvas = WgpuCanvas()
renderer = gfx.renderers.WgpuRenderer(canvas)
# renderer.pixel_ratio = 5
scene = gfx.Scene()

renderer.blend_mode = "weighted_plus"
renderer.pixel_ratio = 3

pygfx_streamlines = np.zeros((1, 3), dtype=np.float32)
for line in range(len(streamlines)):
    curr_line = streamlines.__getitem__(line)
    curr_line = curr_line.astype(np.float32)
    pygfx_streamlines = np.vstack((pygfx_streamlines, curr_line))
    pygfx_streamlines = np.vstack((pygfx_streamlines, np.asarray([np.nan, np.nan, np.nan], dtype=np.float32)))

line = gfx.Line(
    gfx.Geometry(positions=pygfx_streamlines, colors=[(0.1, 1., 1., 0.1)]),
    gfx.LineMaterial(thickness=1.0, opacity=0.1)
)

scene.add(line)

# PICKING INFORMATION
# @line.add_event_handler("pointer_down")            
# def on_pick(event):
#     info = event.pick_info
#     # print(info)
#     if "world_object" in info:
#         vertex_index = info["vertex_index"]
#         print("Vert. Idx: ", vertex_index)
#         print("Vertex Coord: ", pygfx_streamlines[vertex_index])
#         print("Line Object: ", find_line(vertex_index, pygfx_streamlines))


# def find_line(v_index, data):
#     fwd, back = v_index, v_index
#     line_data = [v_index]
#     # while np.array_equal(data[fwd], np.asarray([np.nan, np.nan, np.nan], dtype=np.float32)) is False:
#     while not np.isnan(np.min(data[fwd])):
#         line_data = line_data.append(fwd)
#         fwd += 1
#     # while np.array_equal(data[back], np.asarray([np.nan, np.nan, np.nan], dtype=np.float32)) is False:
#     while not np.isnan(np.min(data[back])):
#         line_data = line_data.append(back)
#         back -= 1
#     return line_data


camera = gfx.PerspectiveCamera(100, 16 / 9)
camera.local.position = (100, 100, 50)
camera.show_pos((0, 0, 0))
controller = gfx.OrbitController(camera, register_events=renderer)
if __name__ == "__main__":
    canvas.request_draw(lambda: renderer.render(scene, camera))
    run()