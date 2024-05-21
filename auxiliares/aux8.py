import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
import math
from pathlib import Path
import utils.transformations as tr
import utils.shapes as shapes

from utils.drawables import DirectionalLight, Material
from utils.scene_graph import SceneGraph
from utils.helpers import Camera, mesh_from_file

WIDTH = 640
HEIGHT = 640

direction = np.array([0, 0, -1])


def normalize(direction):
    return direction/(math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2))


# puntos de control
P = [[-5, 0], [-10, 2.5], [5, 0], [5, 10]]
# parámetro t
t = 0


# controler de siempre


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = {"total_time": 0.0, "camera": None}
        self.init()

    def init(self):
        GL.glClearColor(0.7, 0.7, 0.9, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]

# genera valor para bezier, dados los puntos y el parámetro t


def bezierCurve(t, P0, P1, P2, P3):

    return P0 * pow(1-t, 3) + P1 * 3 * t * pow(1-t, 2) + P2 * 3 * pow(t, 2) * (1-t) + P3 * pow(t, 3)


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 5", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Definimos una camara con su distancia, la medida de la pantalla y el tipo de camara
    controller.program_state["camera"] = Camera(WIDTH, HEIGHT)
    controller.program_state["camera"].position += [0, 3, 10]

    with open(Path(os.path.dirname(__file__)) / "shaders/color_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/color_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()

    pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(color_vertex_source_code, "vertex"),
        pyglet.graphics.shader.Shader(color_fragment_source_code, "fragment")
    )

    # Defino mis objetos

    SharkMesh = mesh_from_file(
        Path(os.path.dirname(__file__)) / "assets/shark.obj")[0]["mesh"]
    SharkMesh.init_gpu_data(pipeline)
    direction = np.array([0, 0, -1])
    # Creo un grafo de escena
    graph = SceneGraph(controller)

    # Agrego todos los objetos al grafo

    graph.add_node("shark",
                   mesh=SharkMesh,
                   pipeline=pipeline,
                   material=Material([0.6, 0.5, 0.9]),
                   rotation=[-np.pi/2, np.pi/2, np.pi],
                   scale=[1.5, 1.5, 1.5]
                   )

    graph.add_node("sun",
                   pipeline=pipeline,
                   light=DirectionalLight(diffuse=[0.4, 0.4, 0.4], specular=[
                                          0, 0.2, 0.5], ambient=[0.6, 0.6, 0.6]),
                   rotation=[-np.pi/2, 0, 0]
                   )

    def update(dt):
        global direction
        global t

        controller.program_state["total_time"] += dt

        # variables del controller
        time = controller.program_state["total_time"]
        camera = controller.program_state["camera"]

        # oscila entre 0 y 1
        t = np.sin(time)*0.5 + 0.5

        # shark Control
        graph["shark"]["position"][0] = bezierCurve(
            t, P[0][0], P[1][0], P[2][0], P[3][0])
        graph["shark"]["position"][1] = bezierCurve(
            t, P[0][1], P[1][1], P[2][1], P[3][1])

        # control de la camara
        # camera.position -= 2 * direction + [0, 1.5, 0]
        camera.focus = camera.position + direction
        direction = normalize(direction)
        # control cow
        if controller.is_key_pressed(pyglet.window.key.A):
            direction -= np.cross(direction, [0.0, 1.0, 0.0]) * 2*dt

        if controller.is_key_pressed(pyglet.window.key.D):
            direction += np.cross(direction, [0.0, 1.0, 0.0]) * 2*dt

        if controller.is_key_pressed(pyglet.window.key.W):
            camera.position += direction * 0.05

        if controller.is_key_pressed(pyglet.window.key.S):
            camera.position -= direction * 0.05

        camera.update()

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()

        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
