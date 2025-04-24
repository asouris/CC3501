# LIBRERIAS
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np

# MODULOS (cuidado con las rutas)
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))


from utils.helpers import init_axis, mesh_from_file
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model

# Controla la ventana
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.light_mode = False


# CAMARA definida en una clase
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 2

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward


# Obtener UV del atlas
def get_atlas_uv(xoffset, yoffset, atlas):
    size = 16
    deltax = 16 / atlas.width
    deltay = 16 / atlas.height

    return [
        deltax*xoffset, deltay*yoffset,
        deltax*(xoffset+1), deltay*yoffset,
        deltax*(xoffset+1), deltay*(yoffset+1),
        deltax*xoffset, deltay*(yoffset+1)
    ]


if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 6")
    controller.set_exclusive_mouse(True)

    # --- Shader con textura ---
    vert_source = """
    #version 330
    in vec3 position;
    in vec2 texCoord; 

    out vec2 fragTexCoord; 

    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);

    void main() {
        fragTexCoord = texCoord;
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """
    frag_source = """
    #version 330
    in vec2 fragTexCoord;
    uniform sampler2D u_texture;
    out vec4 outColor;
    void main() {
        outColor = texture(u_texture, fragTexCoord);
    }
    """

    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))

    # --- Shader de color con alpha ---
    color_vert_source = """
    #version 330
    in vec3 position;

    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);

    void main() {
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """
    color_frag_source = """
    #version 330
    uniform vec4 u_color;
    out vec4 outColor;
    void main() {
        outColor = vec4(u_color);
    }
    """

    color_pipeline = ShaderProgram(Shader(color_vert_source, "vertex"), Shader(color_frag_source, "fragment"))

    # Setup escena
    root = os.path.dirname(__file__)
    cam = MyCam([0,3,0])
    axis = init_axis(cam)

    world = SceneGraph(cam)
    tworld = SceneGraph(cam)

    atlas = Texture(root + "/../../assets/atlas.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST)
    quad = Model(shapes.Square["position"], shapes.Square["uv"], index_data=shapes.Square["indices"])

    tierra = [
        *get_atlas_uv(27, 20, atlas),
        *get_atlas_uv(27, 20, atlas),
        *get_atlas_uv(27, 20, atlas),
        *get_atlas_uv(27, 20, atlas),
        *get_atlas_uv(8, 14, atlas),
        *get_atlas_uv(23, 23, atlas),
    ]
    tierra_cube = Model(shapes.Cube["position"], tierra, index_data=shapes.Cube["indices"])

    tnt = [
        *get_atlas_uv(16, 2, atlas),
        *get_atlas_uv(16, 2, atlas),
        *get_atlas_uv(16, 2, atlas),
        *get_atlas_uv(16, 2, atlas),
        *get_atlas_uv(17, 2, atlas),
        *get_atlas_uv(15, 2, atlas),
    ]
    tnt_cube = Model(shapes.Cube["position"], tnt, index_data=shapes.Cube["indices"])

    hole_positions = {(4, 4), (4, 5), (5, 4), (5, 5)}  # Hoyo 2x2

    for x in range(10):
        for z in range(10):
            if (x, z) in hole_positions:
                continue  # Deja espacio para cubos azules

            name = f"tierra_{x}_{z}"
            world.add_node(name, mesh=tierra_cube, texture=atlas, pipeline=pipeline)
            world[name]["position"] = [x * 0.5, 0, z * 0.5]
            world[name]["scale"] = [0.5, 0.5, 0.5]

    world.add_node("tnt", mesh=tnt_cube, texture=atlas, pipeline=pipeline)
    world["tnt"]["position"] = [1, 0.5, 1]
    world["tnt"]["scale"] = [0.5, 0.5, 0.5]

    zorzal = mesh_from_file(root + "/../../assets/zorzal.obj")
    world.add_node("zorzal_root")
    for m in zorzal:
        world.add_node(m["id"], attach_to="zorzal_root", mesh=m["mesh"], pipeline=pipeline, texture=m["texture"])
        world[m["id"]]["position"] = [2, 3, 2]
        world[m["id"]]["scale"] = [0.7, 0.7, 0.7]

    # Cubos azules translúcidos en el hoyo
    blue_cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])
    for i, (x, z) in enumerate(hole_positions):
        name = f"blue_cube_{i}"
        world.add_node(name, mesh=blue_cube, pipeline=color_pipeline)
        world[name]["position"] = [x * 0.5, 0.0, z * 0.5]
        world[name]["scale"] = [0.5, 0.5, 0.5]
        world[name]["color"] = [0.0, 0.0, 0.8, 0.5]  # Azul con transparencia


    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.7, 0.9, 1, 1)
        glEnable(GL_DEPTH_TEST)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #axis.draw()
        world.draw()
        
        tworld.draw()
        glDisable(GL_BLEND)

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W: cam.direction[0] = 1
        if symbol == key.S: cam.direction[0] = -1
        if symbol == key.A: cam.direction[1] = 1
        if symbol == key.D: cam.direction[1] = -1

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol in (key.W, key.S): cam.direction[0] = 0
        if symbol in (key.A, key.D): cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = math.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)

    def update(dt):
        world.update()
        tworld.update()
        #axis.update()
        cam.time_update(dt)
        controller.time += dt

    clock.schedule_interval(update, 1/60)
    run()
