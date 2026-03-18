#LIBRERIAS
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np
root = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))


#MODULOS (cuidado con las rutas)
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from utils.helpers import init_axis, mesh_from_file
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model, DirectionalLight, Material, PointLight

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

    controller = Controller(1000, 1000,"Auxiliar 8")
    controller.set_exclusive_mouse(True)



    with open(root +  "/shaders/color_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(root +  "/shaders/color_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = Shader(color_vertex_source_code, "vertex")
    frag_program = Shader(color_fragment_source_code, "fragment")
    pipeline = ShaderProgram(vert_program, frag_program)
    root = os.path.dirname(__file__)

    vaca = mesh_from_file(__file__ + "/../../../assets/cow.obj")[0]['mesh']
    quad = Model(shapes.Square["position"], index_data=shapes.Square["indices"], normal_data=shapes.Square["normal"])
    cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"], normal_data=shapes.Cube["normal"])



    cam = MyCam([0,0,1])

    axis = init_axis(cam)

    graph = SceneGraph(cam)

    graph.add_node("luz",
                   pipeline=pipeline,
                   light=DirectionalLight(ambient=[1, 0, 1]))
    
    graph.add_node("vaca",
                            mesh=vaca,
                            pipeline=pipeline,
                            scale=[0.3, 0.3, 0.3],
                            position=[0, 0, 0],
                            material=Material(ambient=[0.2, 0, 1], diffuse=[0.6, 0, 0.6])
                        )
   

    @controller.event
    def on_draw():
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        controller.clear()
        glClearColor(1,1,1,1)
        #axis.draw()
        graph.draw()
        

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
        graph.update()
        axis.update()
        cam.time_update(dt)

        c_pos = cam.position.copy()
        c_pos[1] = 0

        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()