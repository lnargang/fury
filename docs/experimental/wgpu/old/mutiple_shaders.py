import pygfx as gfx
from pygfx.renderers.wgpu import Binding, register_wgpu_render_function, WorldObjectShader
from pygfx.resources import Buffer

import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import imageio.v3 as iio

import pylinalg as la
import numpy as np
import time as time

class CubeMaterial(gfx.Material):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register_wgpu_render_function(gfx.WorldObject, CubeMaterial)
class Shader(WorldObjectShader):
    type = "render"

    def get_bindings(self, wobject, shared):
        geometry = wobject.geometry
        material = wobject.material
        bindings = {
            0: Binding("u_stdinfo", "buffer/uniform", shared.uniform_buffer),
            1: Binding("u_wobject", "buffer/uniform", wobject.uniform_buffer),
            2: Binding("u_material", "buffer/uniform", material.uniform_buffer),
        }
        # to none-indexed geometry
        none_indexed_positions_list = []
        for face in geometry.indices.data:
            none_indexed_positions_list.append(geometry.positions.data[face])
        none_indexed_positions = np.concatenate(none_indexed_positions_list)
        bindings[3] = Binding(
            "s_positions", "buffer/read_only_storage", Buffer(none_indexed_positions)
        )
        self.define_bindings(0, bindings)
        return { 0: bindings, }

    def get_pipeline_info(self, wobject, shared):
        return {
            "primitive_topology": wgpu.PrimitiveTopology.triangle_list,
            "cull_mode": wgpu.CullMode.none,
        }

    def get_render_info(self, wobject, shared):
        geometry = wobject.geometry
        n = geometry.indices.data.size
        return {
            "indices": (n, 1),
            "render_mask": 3,
        }

    def get_code(self):
        return (
            self.code_definitions()
            + self.code_common()
            + self.code_vertex()
            + self.code_fragment()
        )

    def code_vertex(self):
        return """
        struct VertexInput {
            @builtin(vertex_index) vertex_index : u32,
        };

        @vertex
        fn vs_main(in: VertexInput) -> Varyings {
            let index = i32(in.vertex_index);

            let position_xyz = load_s_positions(index);
            let u_mvp = u_stdinfo.projection_transform * u_stdinfo.cam_transform * u_wobject.world_transform;
            let position = u_mvp * vec4<f32>( position_xyz, 1.0 );

            var varyings: Varyings;
            varyings.position = vec4<f32>(position);
            
            return varyings;
        }
        """

    def code_fragment(self):
        return """
        @fragment
        fn fs_main(varyings: Varyings, @builtin(front_facing) is_front: bool) -> FragmentOutput {
            var out: FragmentOutput;

            out.color = vec4<f32>(0.3,0.4,0.3,1.0);

            return out;
        }
        """

class CubeMaterial2(gfx.Material):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register_wgpu_render_function(gfx.WorldObject, CubeMaterial2)
class Shader(WorldObjectShader):
    type = "render"

    def get_bindings(self, wobject, shared):
        geometry = wobject.geometry
        material = wobject.material
        bindings = {
            0: Binding("u_stdinfo", "buffer/uniform", shared.uniform_buffer),
            1: Binding("u_wobject", "buffer/uniform", wobject.uniform_buffer),
            2: Binding("u_material", "buffer/uniform", material.uniform_buffer),
        }
        # to none-indexed geometry
        none_indexed_positions_list = []
        for face in geometry.indices.data:
            none_indexed_positions_list.append(geometry.positions.data[face])
        none_indexed_positions = np.concatenate(none_indexed_positions_list)
        bindings[3] = Binding(
            "s_positions", "buffer/read_only_storage", Buffer(none_indexed_positions)
        )
        self.define_bindings(0, bindings)
        return { 0: bindings, }

    def get_pipeline_info(self, wobject, shared):
        return {
            "primitive_topology": wgpu.PrimitiveTopology.triangle_list,
            "cull_mode": wgpu.CullMode.none,
        }

    def get_render_info(self, wobject, shared):
        geometry = wobject.geometry
        n = geometry.indices.data.size
        return {
            "indices": (n, 1),
            "render_mask": 3,
        }

    def get_code(self):
        return (
            self.code_definitions()
            + self.code_common()
            + self.code_vertex()
            + self.code_fragment()
        )

    def code_vertex(self):
        return """
        struct VertexInput {
            @builtin(vertex_index) vertex_index : u32,
        };

        @vertex
        fn vs_main(in: VertexInput) -> Varyings {
            let index = i32(in.vertex_index);

            let position_xyz = load_s_positions(index);
            let u_mvp = u_stdinfo.projection_transform * u_stdinfo.cam_transform * u_wobject.world_transform;
            let position = u_mvp * vec4<f32>( position_xyz, 1.0 );

            var varyings: Varyings;
            varyings.position = vec4<f32>(position);
            
            return varyings;
        }
        """

    def code_fragment(self):
        return """
        @fragment
        fn fs_main(varyings: Varyings, @builtin(front_facing) is_front: bool) -> FragmentOutput {
            var out: FragmentOutput;

            out.color = vec4<f32>(1.0,0.8,0.2,1.0);

            return out;
        }
        """

# setup
renderer = gfx.WgpuRenderer(WgpuCanvas(size=(640,480)))
scene = gfx.Scene()
# scene geometry
geo = gfx.box_geometry(width=0.5,height=0.5,depth=0.5)

mesh_temp = gfx.Mesh(geo,material=CubeMaterial())
scene.add(mesh_temp)
mesh_temp2 = gfx.Mesh(geo,material=CubeMaterial2())
mesh_temp2.local.x += 1
scene.add(mesh_temp2)

# camera
camera = gfx.PerspectiveCamera(45, 640 / 480)
camera.show_object(scene)
controller = gfx.OrbitController(camera, register_events=renderer)
# lighting
scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

def animate():
    renderer.render(scene=scene, camera=camera)
    renderer.request_draw()

if __name__ == "__main__":
    renderer.request_draw(animate)
    run()