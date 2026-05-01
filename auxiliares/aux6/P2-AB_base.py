#LIBRERIAS
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np

#MODULOS (cuidado con las rutas)
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from utils.helpers import init_axis, mesh_from_file
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model

#Controla la ventana
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.light_mode = False


#CAMARA definida en una clase
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


def get_atlas_uv(xoffset, yoffset, atlas):
    return ""

if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 6")
    controller.set_exclusive_mouse(True)


# Cambio de color a textura
    vert_source = """
#version 330

in vec3 position;


uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

void main() {
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}
    """
    frag_source = """
#version 330

out vec4 outColor;

void main() {
    outColor = vec4(0.0, 1.0, 0.0, 1.0);
}
    """

    # parte A
    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))
    root = os.path.dirname(__file__)

    cam = MyCam([0,2,2])

    world = SceneGraph(cam)

    tierra_cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])

    tnt_cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])

    for x in range(10):
        for z in range(10):
            name = f"tierra_{x}_{z}"
            world.add_node(name, mesh=tierra_cube, pipeline=pipeline)
            world[name]["position"] = [x * 0.5, 0, z * 0.5]
            world[name]["scale"] = [0.5, 0.5, 0.5]

    world.add_node("tnt", mesh=tnt_cube, pipeline=pipeline)
    world["tnt"]["position"] = [1, 2, 1]
    world["tnt"]["scale"] = [0.5, 0.5, 0.5]

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.7,0.9,1,1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        world.draw()
        

    #CAMARA vista en aux5
    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1

        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = math.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)

    #Informacion que se actualiza con el tiempo
    def update(dt):
        world.update()
        cam.time_update(dt)

        c_pos = cam.position.copy()
        c_pos[1] = 0

        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()