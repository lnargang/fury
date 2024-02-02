import pygfx as gfx
import wgpu
from wgpu.gui.auto import WgpuCanvas, run

from wgpu.utils.shadertoy import Shadertoy

shader_text = """

vec2 intersect_AABB(vec3 ray_dir, vec3 rayPos, vec3 boxMin, vec3 boxMax)
{
    vec3 tMin = (boxMin - rayPos);
    tMin.x *= ray_dir.x;
    tMin.y *= ray_dir.y;
    tMin.z *= ray_dir.z;

    vec3 tMax = (boxMax - rayPos);
    tMax.x *= ray_dir.x;
    tMax.y *= ray_dir.y;
    tMax.z *= ray_dir.z;

    vec3 t1;
    vec3 t2;
    if (tMax.x < tMin.x) {
        t1.x = tMax.x;
        t2.x = tMin.x;
    }
    else {
        t2.x = tMax.x;
        t1.x = tMin.x;
    }
    if (tMax.y < tMin.y) {
        t1.y = tMax.y;
        t2.y = tMin.y;
    }
    else {
        t2.y = tMax.y;
        t1.y = tMin.y;
    }
    if (tMax.z < tMin.z) {
        t1.z = tMax.z;
        t2.z = tMin.z;
    }
    else {
        t2.z = tMax.z;
        t1.z = tMin.z;
    }

    float tNear = max(max(t1.x, t1.y), t1.z);
    float tFar  = min(min(t2.x, t2.y), t2.z);

    return vec2(tNear,tFar);
}

vec2 rotate2d(vec2 v, float a) {
	float sinA = sin(a);
	float cosA = cos(a);
	return vec2(v.x * cosA - v.y * sinA, v.y * cosA + v.x * sinA);	
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    float uv_x = fragCoord.x / iResolution.x;
    float uv_y = fragCoord.y / iResolution.y;

    float y_offset = iResolution.x / iResolution.y;

    uv_x = (uv_x*2.0-1.0) * y_offset;
    uv_y = (2.0*uv_y-1.0);

    vec3 col = vec3(0.0);

    vec3 ray_dir = vec3(uv_x,uv_y,1.);
    // norm
    ray_dir /= sqrt(ray_dir.x * ray_dir.x + ray_dir.y * ray_dir.y + ray_dir.z * ray_dir.z);

    vec3 ray_pos = vec3(0,0,-4);
    ray_pos.xz = rotate2d(ray_pos.xz, -iMouse.x * 0.01);
    ray_dir.xz = rotate2d(ray_dir.xz, -iMouse.x * 0.01);
    
    ray_pos.xy = rotate2d(ray_pos.xy, iMouse.y * 0.01);
    ray_dir.xy = rotate2d(ray_dir.xy, iMouse.y * 0.01);

    vec3 one = vec3(1.0);

    vec3 inv_ray_dir = vec3(1.0/ray_dir.x,1.0/ray_dir.y,1.0/ray_dir.z);

    vec3 box_min = vec3(-1.0,-1.0,-1.0);
    vec3 box_max = vec3(1.0,1.0,1.0);

    vec2 dist = intersect_AABB(inv_ray_dir, ray_pos, box_min, box_max);

    if(dist.x < dist.y) {
        col = vec3(0.4);
    }

    fragColor = vec4(col, 1.0);
}

"""

shader_text_fun = """
  const vec3 LP = vec3(-0.6, 0.7, -0.3); 
  const vec3 LC = vec3(.85,0.80,0.70);  
  const vec3 HC1 = vec3(.5, .4, .3);
  const vec3 HC2 = vec3(0.1,.1,.6)*.5; 
  const vec3 HLD = vec3(0,1,0);   
  const vec3 BC = vec3(0.25,0.25,0.25);  
  const vec3 FC = vec3(1.30,1.20,1.00); 
  const float AS = .5; 
  const float DS = 1.; 
  const float BS = .3;   
  const float FS = .3;
  const float MAX_TRACE_DISTANCE = 10.;           
  const float INTERSECTION_PRECISION = 0.0001;   
  const int NUM_OF_TRACE_STEPS = 64;         
  const float STEP_MULTIPLIER = 1.;                
  
  struct Camera {
    vec3 ro;
    vec3 rd;
    vec3 forward;
    vec3 right;
    vec3 up;
    float FOV;
  };
  struct Surface {
    float len;
    vec3 position;
    vec3 colour;
    float id;
    float steps;
    float AO;
  };
  struct Model {
    float dist;
    vec3 colour;
    float id;
  };
  vec2 toScreenspace(in vec2 p) {
    vec2 uv = (p - 0.5 * iResolution.xy) / min(iResolution.y, iResolution.x);
    return uv;
  }
  mat2 R(float a) {
    float c = cos(a);
    float s = sin(a);
    return mat2(c, -s, s, c);
  }
  Camera getCamera(in vec2 uv, in vec3 pos, in vec3 target) {
    vec3 f = normalize(target - pos);
    vec3 r = normalize(vec3(f.z, 0., -f.x));
    vec3 u = normalize(cross(f, r));
    
    float FOV = 1.+cos(iTime*.1)*.8;
    
    return Camera(
      pos,
      normalize(f + FOV * uv.x * r + FOV * uv.y * u),
      f,
      r,
      u,
      FOV
    );
  }
  float G( vec3 p ) {
    return dot(sin(p.yzx), cos(p.zxy));
  }
  Model model(vec3 p) {
    float t = iTime*.1;
    p.xz *= R(t);
    p.xy *= R(.3);
    p.xy -= .5;
    float d = abs(-(length(vec2(p.y, length(p.xz)-2.))-1.8+cos(t)*.3));
    float g = G(p.yxz*4.)/4.;
    
    d=length(vec2(d,g))-.3;
    vec3 colour = vec3(g);
    
    return Model(d, colour, 1.);
  }
  Model map( vec3 p ){
    return model(p);
  }
  vec3 calcNormal( in vec3 pos ){
    vec3 eps = vec3( 0.001, 0.0, 0.0 );
    vec3 nor = vec3(
      map(pos+eps.xyy).dist - map(pos-eps.xyy).dist,
      map(pos+eps.yxy).dist - map(pos-eps.yxy).dist,
      map(pos+eps.yyx).dist - map(pos-eps.yyx).dist );
    return normalize(nor);
  }
  Surface march( in Camera cam ){
    float h = 1e4; // local distance
    float d = 0.; // ray depth
    float id = -1.; // surace id
    float s = 0.; // number of steps
    float ao = 0.; // march space AO. Simple weighted accumulator. Not really AO, but ¯\_(ツ)_/¯
    vec3 p; // ray position
    vec3 c; // surface colour

    for( int i=0; i< NUM_OF_TRACE_STEPS ; i++ ) {
      if( abs(h) < INTERSECTION_PRECISION || d > MAX_TRACE_DISTANCE ) break;
      p = cam.ro+cam.rd*d;
      Model m = map( p );
      h = m.dist;
      d += h * STEP_MULTIPLIER;
      id = m.id;
      s += 1.;
      ao += max(h, 0.);
      c = m.colour;
    }

    if( d >= MAX_TRACE_DISTANCE ) id = -1.0;

    return Surface( d, p, c, id, s, ao );
  }

  float softshadow( in vec3 ro, in vec3 rd, in float mint, in float tmax ) {
    float res = 1.0;
    float t = mint;
    for( int i=0; i<16; i++ ) {
      float h = map( ro + rd*t ).dist;
      res = min( res, 8.0*h/t );
      t += clamp( h, 0.02, 0.10 );
      if( h<0.001 || t>tmax ) break;
    }
    return clamp( res, 0.0, 1.0 );
  }
  float AO( in vec3 pos, in vec3 nor ) {
    float occ = 0.0;
    float sca = 1.0;
    for( int i=0; i<5; i++ )
    {
      float hr = 0.01 + 0.12*float(i)/4.0;
      vec3 aopos =  nor * hr + pos;
      float dd = map( aopos ).dist;
      occ += -(dd-hr)*sca;
      sca *= 0.95;
    }
    return clamp( 1.0 - 3.0*occ, 0.0, 1.0 );    
  }
  vec3 shade(vec3 col, vec3 pos, vec3 nor, vec3 ref, Camera cam) {
    
    vec3 plp = LP - pos; // point light
    
    float o = AO( pos, nor );                 // Ambient occlusion
    vec3  l = normalize( plp );                    // light direction
    
    float d = clamp( dot( nor, l ), 0.0, 1.0 )*DS;   // diffuse component
    float b = clamp( dot( nor, normalize(vec3(-l.x,0,-l.z))), 0.0, 1.0 )*clamp( 1.0-pos.y,0.0,1.0)*BS; // back light component
    float f = pow( clamp(1.0+dot(nor,cam.rd),0.0,1.0), 2.0 )*FS; // fresnel component

    vec3 c = vec3(0.0);
    c += d*LC;                           // diffuse light integration
    c += mix(HC1,HC2,dot(nor, HLD))*AS;        // hemisphere light integration (ambient)
    c += b*BC*o;       // back light integration
    c += f*FC*o;       // fresnel integration
    
    return col*c;
  }
  vec3 render(Surface surface, Camera cam, vec2 uv) {
    vec3 colour = vec3(.04,.045,.05);
    colour = vec3(.35, .5, .75);
    vec3 colourB = vec3(.9, .85, .8);
    
    colour = mix(colourB, colour, pow(length(uv), 2.)/1.5);

    if (surface.id > -1.){
      vec3 surfaceNormal = calcNormal( surface.position );
      vec3 ref = reflect(cam.rd, surfaceNormal);
      colour = surfaceNormal;
      vec3 pos = surface.position;
      
      float t = iTime;
      vec3 col = mix(
        mix(
          vec3(.8,.3,.6), 
          vec3(.6,.3,.8), 
          dot(surfaceNormal,surfaceNormal.zxy)
        ),
        vec3(1), 
        smoothstep(0., .1, cos(surface.colour.r*40.))
      );
      
      colour = shade(col, pos, surfaceNormal, ref, cam);
    }

    return colour;
  }
  
  void mainImage( out vec4 fragColor, in vec2 fragCoord ) {
    vec3 c = vec3(0);
    for(int x=0; x<2; x++) {
      for(int y=0; y<2; y++) {
        vec2 uv = toScreenspace(fragCoord+vec2(x,y)*.5);

        Camera cam = getCamera(uv, vec3(1.5, 0, 1.5), vec3(0));
        Surface surface = march(cam);

        c += render(surface, cam, uv);
      }
    }
    
    fragColor = vec4(c*.5,1);
  }

"""

# does geometry merging work??
# difficult to access geometries/utils.py -> maybe try to reimplement?

shader = Shadertoy(shader_code=shader_text_fun, resolution=(1280,720))

if __name__ == "__main__":
    shader.show()