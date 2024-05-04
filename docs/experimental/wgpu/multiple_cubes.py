import pygfx as gfx
import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import pylinalg as la

canvas = WgpuCanvas(size=(640,480))
renderer = gfx.WgpuRenderer(canvas)
scene = gfx.Scene()
geo = gfx.box_geometry(width=0.5, height=0.5, depth=0.5)

for i in range(10):
    mesh_temp = gfx.Mesh(geo, gfx.MeshPhongMaterial(color="#ffffff"))
    scene.add(mesh_temp)
    pass

mesh_temp = gfx.InstancedMesh(geo, gfx.MeshPhongMaterial(color="#ffffff"), 100)
scene.add(mesh_temp)

for y in range(10):
    for x in range(10):
        m = la.mat_from_translation((y * 2, x * 2, 0))
        mesh_temp.set_matrix_at(x + y * 10, m)

camera = gfx.PerspectiveCamera(45, 640 / 480)
camera.show_object(scene)
controller = gfx.OrbitController(camera=camera,enabled=True, register_events=renderer)

scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight()))

def animate():
    # rot = la.quat_from_euler((0.0071, 0.01), order="XY")
    # mesh_temp.local.rotation = la.quat_mul(rot, mesh_temp.local.rotation)

    renderer.render(scene=scene, camera=camera)
    canvas.request_draw()

if __name__ == "__main__":
    canvas.request_draw(animate)
    run()

'''
import numpy as np
import wgpu
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx
from pygfx.renderers.wgpu import Binding, register_wgpu_render_function
from pygfx.resources import Buffer
from pygfx.renderers.wgpu.meshshader import WorldObjectShader

class WireframeMaterial(gfx.Material):
    uniform_type = dict(
        gfx.Material.uniform_type,
        thickness="f4",
    )

    def __init__(self, *, thickness=1.0, **kwargs):
        super().__init__(**kwargs)
        self.thickness = thickness

    @property
    def thickness(self):
        return self.uniform_buffer.data["thickness"]

    @thickness.setter
    def thickness(self, thickness):
        self.uniform_buffer.data["thickness"] = thickness
        self.uniform_buffer.update_range(0, 1)

@register_wgpu_render_function(gfx.WorldObject, WireframeMaterial)
class WireframeShader(WorldObjectShader):
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

        return {
            0: bindings,
        }

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
        # print(self.code_definitions())
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

            var center: vec3<f32>;
            if(index % 3 == 0) {
                center = vec3<f32>( 1.0, 0.0, 0.0 );
            }else if(index % 3 == 1) {
                center = vec3<f32>( 0.0, 1.0, 0.0 );
            }else {
                center = vec3<f32>( 0.0, 0.0, 1.0 );
            }

            var varyings: Varyings;
            varyings.position = vec4<f32>(position);
            varyings.center = vec3<f32>(center);
            return varyings;
        }
        """

    def code_fragment(self):
        return """

        @fragment
        fn fs_main(varyings: Varyings, @builtin(front_facing) is_front: bool) -> FragmentOutput {
            let center = varyings.center;
            var out: FragmentOutput;
            let afwidth = fwidth( center.xyz );
            let thickness = u_material.thickness;

            let edge3 = smoothstep( ( thickness - 1.0 ) * afwidth, thickness * afwidth, center.xyz );

            let edge = 1.0 - min( min( edge3.x, edge3.y ), edge3.z );

            if ( edge > 0.01 ) {
                if ( is_front ) {
                    out.color = vec4<f32>( 0.9, 0.9, 1.0, 1.0 );
                }else {
                    out.color = vec4<f32>( 0.4, 0.4, 0.5, 0.5);
                }
            } else {
                // discard;
            }

            out.color = vec4<f32>(0.1, 0.2, 0.3, 1.0);

            return out;
        }
        """


renderer = gfx.WgpuRenderer(WgpuCanvas(size=(640, 480)))

thickness = 2

g = gfx.sphere_geometry(1, 16)

mesh1 = gfx.Mesh(g, WireframeMaterial(thickness=thickness))
mesh1.local.x = -1

print(WireframeShader(mesh1).get_code())

mesh2 = gfx.Mesh(
    g, gfx.MeshPhongMaterial(wireframe=True, wireframe_thickness=thickness)
)

mesh2.local.x = 1

scene = gfx.Scene()
scene.add(mesh1, mesh2)

camera = gfx.PerspectiveCamera(45, 640 / 480)
camera.show_object(scene)
controller = gfx.OrbitController(camera, register_events=renderer)

scene.add(gfx.AmbientLight())
scene.add(camera.add(gfx.DirectionalLight(0.7)))


def animate():
    renderer.render(scene, camera)
    renderer.request_draw()


if __name__ == "__main__":
    renderer.request_draw(animate)
    run()
'''