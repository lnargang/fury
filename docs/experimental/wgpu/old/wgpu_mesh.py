import wgpu
from wgpu.gui.auto import WgpuCanvas, run

import numpy as np

canvas = WgpuCanvas(size=(640,480), title="wgpu_mesh.py")

# device info
adapter = wgpu.gpu.request_adapter(power_preference="high-performance")
device = adapter.request_device()

# set up rendering context
context = canvas.get_context()
text_format = context.get_preferred_format(device.adapter)
context.configure(device=device, format=text_format)

# data
vertex_data = np.array(
    [
        # data for a triangle, three points
        [-0.5, -0.5, 0.0],
        [0.5, -0.5, 0.0],
        [0.0, 0.5, 0.0]
    ],
    dtype=np.float32
)

index_data = np.array(
    [0, 1, 2],
    dtype=np.float32
).flatten()

cube_data = np.array(
    [
        # top
        [-1,-1, 1],
        [ 1,-1, 1],
        [ 1, 1, 1],
        [-1, 1, 1],
        # bottom
        [-1, 1,-1],
        [ 1, 1,-1],
        [ 1,-1,-1],
        [-1,-1,-1],
        # right
        [ 1,-1,-1],
        [ 1, 1,-1],
        [ 1, 1, 1],
        [ 1,-1, 1],
        # left
        [-1,-1, 1],
        [-1, 1, 1],
        [-1, 1,-1],
        [-1,-1,-1],
        # front
        [ 1, 1,-1],
        [-1, 1,-1],
        [-1, 1, 1],
        [ 1, 1, 1],
        # back
        [ 1,-1, 1],
        [-1,-1, 1],
        [-1,-1,-1],
        [ 1,-1,-1],
        # done :)
    ],
    dtype=np.float32
)

cube_index = np.array(
    [
        [0, 1, 2, 2, 3, 0],  # top
        [4, 5, 6, 6, 7, 4],  # bottom
        [8, 9, 10, 10, 11, 8],  # right
        [12, 13, 14, 14, 15, 12],  # left
        [16, 17, 18, 18, 19, 16],  # front
        [20, 21, 22, 22, 23, 20],  # back
    ],
    dtype=np.float32
).flatten()

uniform_dtype = [("transform", "float32", (4,4))]
uniform_data = np.zeros((), dtype=uniform_dtype)

vertex_buffer = device.create_buffer_with_data(
    data=vertex_data, usage=wgpu.BufferUsage.VERTEX
)

index_buffer = device.create_buffer_with_data(
    data=index_data, usage=wgpu.BufferUsage.INDEX
)

shader_source = """
struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};
struct VertexOutput {
    @location(0) color : vec4<f32>,
    @builtin(position) pos: vec4<f32>,
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var positions = array<vec2<f32>, 3>(
        vec2<f32>(0.5, -0.5),
        vec2<f32>(-0.5, -0.5),
        vec2<f32>(0.0, 0.75),
    );
    var colors = array<vec3<f32>, 3>(  // srgb colors
        vec3<f32>(1.0, 1.0, 0.0),
        vec3<f32>(1.0, 0.0, 1.0),
        vec3<f32>(0.0, 1.0, 1.0),
    );
    let index = i32(in.vertex_index);
    var out: VertexOutput;
    out.pos = vec4<f32>(positions[index], 0.0, 1.0);
    out.color = vec4<f32>(colors[index], 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let physical_color = pow(in.color.rgb, vec3<f32>(2.2));  // gamma correct
    return vec4<f32>(physical_color, in.color.a);
}
"""

# actually, maybe unecessary? check wgpu.PrimitiveTopology

shader = device.create_shader_module(code=shader_source)

sampler = device.create_sampler()

# pipeline stuff
pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[])

render_pipeline = device.create_render_pipeline(
    layout=pipeline_layout,
    vertex={
        "module": shader,
        "entry_point": "vs_main",
        "buffers": [],
    },
    primitive={
        "topology": wgpu.PrimitiveTopology.triangle_list,
        "front_face": wgpu.FrontFace.ccw,
        "cull_mode": wgpu.CullMode.none,
    },
    depth_stencil=None,
    multisample=None,
    fragment={
        "module": shader,
        "entry_point": "fs_main",
        "targets": [
            {
                "format": text_format,
                "blend": {
                    "color": (
                        wgpu.BlendFactor.one,
                        wgpu.BlendFactor.zero,
                        wgpu.BlendOperation.add,
                    ),
                    "alpha": (
                        wgpu.BlendFactor.one,
                        wgpu.BlendFactor.zero,
                        wgpu.BlendOperation.add,
                    ),
                },
            },
        ],
    },
)


# set up rendering function
def render_frame():
    current_text = context.get_current_texture()
    command_encoder = device.create_command_encoder()

    render_pass = command_encoder.begin_render_pass(
        color_attachments=[
            {
                "view" : current_text.create_view(),
                "resolve_target" : None,
                "clear_value" : (0,0,0,1),
                "load_op" : wgpu.LoadOp.clear,
                "store_op" : wgpu.StoreOp.store,
            }
        ],
    )

    render_pass.set_pipeline(render_pipeline)

    render_pass.set_vertex_buffer(0, vertex_buffer)

    render_pass.draw(3,1,0,0)
    render_pass.end()
    device.queue.submit([command_encoder.finish()])
    canvas.request_draw()


if __name__ == "__main__":
    canvas.request_draw(render_frame)
    run()