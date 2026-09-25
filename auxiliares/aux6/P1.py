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

if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 6")
    controller.set_exclusive_mouse(True)


    vert_source = """
#version 330

in vec3 position;

// nuevo input, para cada vertice se recibe una coordenada 2D
in vec2 texCoord; 

// no se hace nada en el vertex, pero se manda al fragment
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

// se recibe la coordenada 2D
in vec2 fragTexCoord;

// y una imagen
uniform sampler2D u_texture;

out vec4 outColor;

void main() {
    // aqui la función texture() recibe la imagen y la coordenada
    // esta funcion devuelve el color de la imagen en la coordenada indicada
    outColor = texture(u_texture, fragTexCoord);
}
    """

    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))
    root = os.path.dirname(__file__)

    cam = MyCam([0,0,2])

    world = SceneGraph(cam)

    # intercambiar entre gl_nearest y gl_linear, ver el efecto cuando se acerca
    sandImage = Texture(root + "/../../assets/Sand 002_COLOR.jpg", minFilterMode=GL_LINEAR, maxFilterMode=GL_LINEAR)

    # 4 coordenadas para cada vertice de una cara. Cada coordenada con 2 numeros (u, v)
    face_uv = [0, 0, 1, 0, 1, 1, 0, 1]

    # Lo mismo 6 veces para cada cara del cubo
    texcoords = face_uv * 6
    cube = Model(shapes.Cube["position"], texcoords, index_data=shapes.Cube["indices"])

    # Aquí asignamos la textura
    world.add_node("sand", mesh=cube, texture=sandImage, pipeline=pipeline)

    world["sand"]["position"] = [0, 0, 0]
    world["sand"]["scale"] = [1, 1, 1]

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(1,1,1,1)

        # las siguientes lineas activan la obtención de la profundidad
        glEnable(GL_DEPTH_TEST)
        # la capacidad para mezclar colores, en función de su transparencia
        glEnable(GL_BLEND)
        # y como es que esos colores se mezclarán
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # lo dibujamos
        world.draw()
        

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