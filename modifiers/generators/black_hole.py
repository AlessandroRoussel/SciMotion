_name_id = "black_hole"
_title = "Black hole"
_flags = []


def _apply(_render_context):
    gl_context = _render_context.get_gl_context()
    width = _render_context.get_width()
    height = _render_context.get_height()

    glsl_code = """
    #version 430

    layout (local_size_x = 16, local_size_y = 16) in;
    layout (rgba32f, binding = 0) uniform readonly image2D img_input;
    layout (rgba32f, binding = 1) uniform writeonly image2D img_output;

    uniform float iTime;

    #define PI 3.1415926538

    float camR = 30.;     // camera distance
    float tilt = .1;      // camera tilt
    float zoom = 1.5;     // camera zoom

    float a = .6;         // spin parameter (J/M²)
    float discMin = 3.83; // disc inner radius (ISCO)
    float discMax = 15.;  // disc outer radius

    float eps = .01;      // hamiltonian gradient step
    float dtau = .1;      // affine step
    int maxSteps = 500;   // maximum steps

    mat4 diag(vec4 vec){
        return mat4(vec.x,0,0,0,
                    0,vec.y,0,0,
                    0,0,vec.z,0,
                    0,0,0,vec.w);
    }

    float rFromCoords(vec4 pos){
        vec3 p = pos.yzw;
        float rho2 = dot(p,p)-a*a;
        float r2 = .5*(rho2+sqrt(rho2*rho2+4.*a*a*p.z*p.z));
        return sqrt(r2);
    }

    mat4 metric(vec4 pos){
        float r = rFromCoords(pos);
        vec4 k = vec4(-1.,(r*pos.y-a*pos.z)/(r*r+a*a),(r*pos.z+a*pos.y)/(r*r+a*a),pos.a/r);
        float f = 2.*r/(r*r+a*a*pos.a*pos.a/r/r);
        return f*mat4(k.x*k,k.y*k,k.z*k,k.w*k)+diag(vec4(-1,1,1,1));
    }

    float hamiltonian(vec4 x, vec4 p){
        return .5*dot(inverse(metric(x))*p,p);
    }

    vec4 hamiltonianGradient(vec4 x, vec4 p){
        return (vec4(hamiltonian(x+vec4(eps,0,0,0),p),
                    hamiltonian(x+vec4(0,eps,0,0),p),
                    hamiltonian(x+vec4(0,0,eps,0),p),
                    hamiltonian(x+vec4(0,0,0,eps),p))-hamiltonian(x,p))/eps;
    }

    void transportStep(inout vec4 x, inout vec4 p){
        float r = rFromCoords(x);
        float stepsize = dtau;
        p -= stepsize*hamiltonianGradient(x,p);
        x += stepsize*inverse(metric(x))*p;
    }

    bool stopCondition(vec4 pos){
        float r = rFromCoords(pos);
        return r < 1.+sqrt(1.-a*a) || r > max(2.*camR,30.);
    }

    vec4 unit(vec4 vec, mat4 g){
        float norm2 = dot(g*vec,vec);
        if(norm2 != 0.){
            return vec/sqrt(abs(norm2));
        }else{
            return vec;
        }
    }

    mat4 tetrad(vec4 x, vec4 time, vec4 aim, vec4 vert){
        mat4 g = metric(x);
        vec4 E0 = unit(time, g);
        vec4 E1 = unit(aim+dot(g*aim,E0)*E0, g);
        vec4 E3 = unit(vert-dot(g*vert,E1)*E1+dot(g*vert,E0)*E0, g);
        vec4 E2 = unit(inverse(g)*vec4(dot(E0.yzw,cross(E1.yzw,E3.yzw)),
                                    -dot(E0.zwx,cross(E1.zwx,E3.zwx)),
                                    dot(E0.wxy,cross(E1.wxy,E3.wxy)),
                                    -dot(E0.xyz,cross(E1.xyz,E3.xyz))), g);
        mat4 tetrad;
        tetrad[0] = E0;
        tetrad[1] = E1;
        tetrad[2] = E2;
        tetrad[3] = E3;
        return tetrad;
    }

    void main()
    {
        vec2 coords = vec2(gl_GlobalInvocationID.xy);
        vec2 dimensions = vec2(imageSize(img_output).xy);
        if(any(greaterThan(coords, dimensions))){return;}
        vec2 uv = (2.*coords-dimensions.xy)/dimensions.x;
        
        tilt = sin(iTime*.5)*.5;

        float x = sqrt(camR*camR+a*a)*cos(tilt);
        float z = camR*sin(tilt);
        vec4 camPos = vec4(0.,x,0.,z);

        vec4 time = vec4(1.,0.,0.,0.);
        vec4 aim = vec4(0.,x,0.,z);
        vec4 vert = vec4(0.,-x*z,0.,x*x)*sign(cos(tilt));
        mat4 axes = tetrad(camPos, time, aim, vert);
        
        vec4 pos = camPos;
        vec3 dir = normalize(vec3(-zoom,uv));
        vec4 dir4D = -axes[0]+dir.x*axes[1]+dir.y*axes[2]+dir.z*axes[3];
        
        bool captured = false;
        bool hitDisc = false;
        vec4 intersectPos;
        vec2 discUV;
        float blueshift;
 
        vec4 p = metric(pos)*dir4D;
        for(int i=0; i<maxSteps; i++){
            vec4 lastpos = pos;
            transportStep(pos, p);
            if(pos.a*lastpos.a < 0.){

                intersectPos = (pos*abs(lastpos.a)+lastpos*abs(pos.a))/abs(lastpos.a-pos.a);
                float r = rFromCoords(intersectPos);
                if(r > discMin && r < discMax){
                    hitDisc = true;
                    discUV = (intersectPos.yz/discMax+1.)*.5;
                    vec4 discVel = vec4(r+a/sqrt(r),vec3(-intersectPos.z,intersectPos.y,0.)*sign(a)/sqrt(r))/sqrt(r*r-3.*r+2.*a*sqrt(r));
                    blueshift = 1./dot(p,discVel);
                    break;
                }
            }

            if(stopCondition(pos)){
                float r = rFromCoords(pos);
                captured = r < 1.+sqrt(1.-a*a);
                break;
            }
        }

        dir4D = inverse(metric(pos))*p;
        vec3 cubeVec = vec3(-dir4D.y,dir4D.a,-dir4D.z);
        vec4 color = vec4(0);
        if(hitDisc){
            ivec2 discXY = ivec2(discUV*vec2(imageSize(img_input)));
            color = imageLoad(img_input, discXY)*pow(blueshift,3.);
        }
        imageStore(img_output, ivec2(coords), color);
    }
    """

    compute_shader = gl_context.compute_shader(glsl_code)
    compute_shader["iTime"] = _render_context.get_sequence_context().get_current_frame()/35

    _render_context.get_src_texture().bind_to_image(0, read=True, write=False)
    _render_context.get_dest_texture().bind_to_image(1, read=False, write=True)
    compute_shader.run(width//16+1, height//16+1, 1)
