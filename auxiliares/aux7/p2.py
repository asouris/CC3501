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
from utils.drawables import Texture, Model, DirectionalLight, Material, PointLight, SpotLight

#VENTANA
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.sirens_on = True
        self.is_metallic = False
        self.sun_on = True

#CAMARA definida en una clase
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 3

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":

    controller = Controller(1000, 800, "Auxiliar 7")
    controller.set_exclusive_mouse(True)

    with open(root + "/shaders/textured_mesh_lit.vert") as f:
        vertex_source = f.read()

    with open(root + "/shaders/textured_mesh_lit.frag") as f:
        fragment_source = f.read()

    #Se define el pipeline
    vert_program = Shader(vertex_source, "vertex")
    frag_program = Shader(fragment_source, "fragment")
    pipeline = ShaderProgram(vert_program, frag_program)

    #Mallas y textura
    road_mesh = mesh_from_file(root + "/assets/city/road_straight.obj")[0]['mesh']
    chassis_mesh = mesh_from_file(root + "/assets/city/car_police.obj")[0]['mesh']

    texture = Texture(root + "/assets/city/citybits_texture.png")

    mat_calle = Material(ambient=[0.35, 0.35, 0.35], diffuse=[0.9, 0.9, 0.9], specular=[0.25, 0.25, 0.25], shininess=16.0)
    mat_auto = Material(ambient=[0.5, 0.5, 0.5], diffuse=[1.0, 1.0, 1.0], specular=[0.5, 0.5, 0.5], shininess=32.0)

    cam = MyCam(np.array([0.0, 0.8, 2.5]))
    axis = init_axis(cam)
    graph = SceneGraph(cam)

    #Luces
    graph.add_node("sol",
                   pipeline=pipeline,
                   rotation=[-np.pi/3, np.pi/4, 0.0],
                   light=DirectionalLight(ambient=[0.3, 0.3, 0.35], diffuse=[0.8, 0.8, 0.75], specular=[0.5, 0.5, 0.5]))

    graph.add_node("sirena_roja",
                   pipeline=pipeline,
                   position=[-0.15, 0.5, 0.0],
                   light=PointLight(ambient=[0.2, 0.0, 0.0], diffuse=[2.5, 0.1, 0.1], specular=[2.0, 0.3, 0.3], linear=0.03, quadratic=0.01))

    graph.add_node("sirena_azul",
                   pipeline=pipeline,
                   position=[0.15, 0.5, 0.0],
                   light=PointLight(ambient=[0.0, 0.0, 0.2], diffuse=[0.1, 0.3, 2.5], specular=[0.3, 0.3, 2.0], linear=0.03, quadratic=0.01))

    #Modelos
    graph.add_node("calle_1",
                   mesh=road_mesh,
                   pipeline=pipeline,
                   texture=texture,
                   material=mat_calle,
                   position=[0.0, -0.25, -0.65],
                   scale=[1.2, 1.2, 1.2])

    graph.add_node("calle_2",
                   mesh=road_mesh,
                   pipeline=pipeline,
                   texture=texture,
                   material=mat_calle,
                   position=[0.0, -0.25, 1.0],
                   scale=[1.2, 1.2, 1.2])

    graph.add_node("calle_3",
                   mesh=road_mesh,
                   pipeline=pipeline,
                   texture=texture,
                   material=mat_calle,
                   position=[0.0, -0.25, 2.68],
                   scale=[1.2, 1.2, 1.2])

    graph.add_node("carroceria",
                   mesh=chassis_mesh,
                   pipeline=pipeline,
                   texture=texture,
                   material=mat_auto,
                   scale=[1.3, 1.3, 1.3],
                   position=[0.0, 0.0, 0.0],
                   rotation=[0.0, 0.0, 0.0])

    @controller.event
    def on_draw():
        glClearColor(0.04, 0.05, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        controller.clear()

        graph.draw()

    #CONTROLES
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

        if symbol == key.K:
            controller.sun_on = not controller.sun_on
            if controller.sun_on:
                graph["sol"]["light"].ambient = np.array([0.3, 0.3, 0.35], dtype=np.float32)
                graph["sol"]["light"].diffuse = np.array([0.8, 0.8, 0.75], dtype=np.float32)
                graph["sol"]["light"].specular = np.array([0.5, 0.5, 0.5], dtype=np.float32)
            else:
                graph["sol"]["light"].ambient = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sol"]["light"].diffuse = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sol"]["light"].specular = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        if symbol == key.B:
            controller.sirens_on = not controller.sirens_on
            if not controller.sirens_on:
                graph["sirena_roja"]["light"].specular = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sirena_roja"]["light"].diffuse = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sirena_roja"]["light"].ambient = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sirena_azul"]["light"].specular = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sirena_azul"]["light"].diffuse = np.array([0.0, 0.0, 0.0], dtype=np.float32)
                graph["sirena_azul"]["light"].ambient = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        if symbol == key.M:
            controller.is_metallic = not controller.is_metallic
            if controller.is_metallic:
                mat_auto.specular = [2.5, 2.5, 2.5]
                mat_auto.shininess = 250.0
            else:
                mat_auto.specular = [0.3, 0.3, 0.3]
                mat_auto.shininess = 15.0

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

    #CICLO DE ACTUALIZACIÓN
    def update(dt):
        graph.update()
        axis.update()
        cam.time_update(dt)

        if controller.sirens_on:
            radio_baliza = 0.22
            vel = 9.0
            bx = radio_baliza * np.cos(controller.time * vel)
            bz = radio_baliza * np.sin(controller.time * vel)
            graph["sirena_roja"]["position"] = [bx, 0.5, bz]
            graph["sirena_azul"]["position"] = [-bx, 0.5, -bz]

            graph["sirena_roja"]["light"].diffuse = np.array([2.5, 0.1, 0.1], dtype=np.float32)
            graph["sirena_roja"]["light"].ambient = np.array([0.4, 0.0, 0.0], dtype=np.float32)
            graph["sirena_azul"]["light"].diffuse = np.array([0.1, 0.3, 2.5], dtype=np.float32)
            graph["sirena_azul"]["light"].ambient = np.array([0.0, 0.0, 0.4], dtype=np.float32)

        controller.time += dt

    clock.schedule_interval(update, 1/60)
    run()