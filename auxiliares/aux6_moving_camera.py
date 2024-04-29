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

direction = np.array([1, 1, 1])


def normalize(direction):
    return direction/(math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2))


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
        GL.glClearColor(0, 0, 0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)

    def is_key_pressed(self, key):
        return self.key_handler[key]


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 5", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Definimos una camara con su distancia, la medida de la pantalla y el tipo de camara
    controller.program_state["camera"] = Camera(WIDTH, HEIGHT)

    with open(Path(os.path.dirname(__file__)) / "shaders/color_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/color_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()

    pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(color_vertex_source_code, "vertex"),
        pyglet.graphics.shader.Shader(color_fragment_source_code, "fragment")
    )

    # Defino mis objetos

    cowMesh = mesh_from_file("assets/cow.obj")[0]["mesh"]
    cowMesh.init_gpu_data(pipeline)
    direction = np.array([1, 0, 0])
    # Creo un grafo de escena
    graph = SceneGraph(controller)

    # Agrego todos los objetos al grafo

    graph.add_node("cow",
                   mesh=cowMesh,
                   pipeline=pipeline,
                   material=Material()
                   )
    graph.add_node("cow2",
                   mesh=cowMesh,
                   position=[2, 0, 0.5],
                   pipeline=pipeline,
                   material=Material())

    graph.add_node("sun",
                   pipeline=pipeline,
                   light=DirectionalLight(diffuse=[0.4, 0.4, 0.4], specular=[0, 0, 0], ambient=[0.6, 0.6, 0.6]))

    def update(dt):
        global direction
        controller.program_state["total_time"] += dt
        # variables del controller
        time = controller.program_state["total_time"]
        camera = controller.program_state["camera"]

        # control de la camara
        camera.position = np.array([2*np.sin(time), 0, 2*np.cos(
            time)]) + np.array([0, np.sin(time), 0])

        direction = normalize(direction)

        # control cow
        if controller.is_key_pressed(pyglet.window.key.A):
            direction -= np.cross(direction, [0.0, 1.0, 0.0]) * 2*dt
            graph["cow"]["rotation"] += [0, 2*dt, 0]

        if controller.is_key_pressed(pyglet.window.key.D):
            direction += np.cross(direction, [0.0, 1.0, 0.0]) * 2*dt
            graph["cow"]["rotation"] += [0, -2*dt, 0]

        if controller.is_key_pressed(pyglet.window.key.W):
            graph["cow"]["position"] += direction * 0.05

        if controller.is_key_pressed(pyglet.window.key.S):
            graph["cow"]["position"] -= direction * 0.05

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
