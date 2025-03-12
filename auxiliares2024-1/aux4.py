import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
from pathlib import Path
import utils.transformations as tr
import utils.shapes as shapes
# se agregó SceneGraph y OrbitCamera (y camera) a helpers
from utils.helpers import Model, Mesh, SceneGraph, OrbitCamera

WIDTH = 640
HEIGHT = 640

# controler de siempre


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = {"total_time": 0.0}
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
    controller = Controller("Auxiliar 4", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Definimos una camara con su distancia, la medida de la pantalla y el tipo de camara
    camera = OrbitCamera(2, WIDTH, HEIGHT, "perspective")
    # seteamos su angulo
    camera.phi = np.pi / 4
    camera.theta = np.pi / 4

    with open(Path(os.path.dirname(__file__)) / "shaders/color_mesh.vert") as f:
        color_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/color_mesh.frag") as f:
        color_fragment_source_code = f.read()

    pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(color_vertex_source_code, "vertex"),
        pyglet.graphics.shader.Shader(color_fragment_source_code, "fragment")
    )

    # Defino mis objetos
    cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])
    cube.init_gpu_data(pipeline)

    # Creo un grafo de escena
    graph = SceneGraph(camera)

    # Agrego todos los objetos al grafo
    graph.add_node("body")
    graph.add_node("chest",
                   attach_to="body",
                   mesh=cube,
                   color=[1, 0, 0],
                   scale=[0.5, 1, 0.35]
                   )
    graph.add_node("head",
                   attach_to="body",
                   mesh=cube,
                   color=[0, 1, 1],
                   position=[0, 0.75, 0],
                   scale=[0.35, 0.35, 0.35]
                   )
    graph.add_node("left_arm",
                   attach_to="body",
                   mesh=cube,
                   color=[0, 1, 0],
                   position=[-0.5, 0, 0],
                   rotation=[0, 0, -0.5],
                   scale=[0.2, 1, 0.2]
                   )
    graph.add_node("right_arm",
                   attach_to="body",
                   mesh=cube,
                   color=[0, 1, 0],
                   position=[0.5, 0, 0],
                   rotation=[0, 0, 0.5],
                   scale=[0.2, 1, 0.2],
                   )
    graph.add_node("left_leg", attach_to="body")
    graph.add_node("right_leg", attach_to="body")
    graph.add_node("left_upper_leg",
                   attach_to="left_leg",
                   mesh=cube,
                   color=[0, 0, 1],
                   position=[-0.2, -0.85, 0],
                   rotation=[0, 0, -0.15],
                   scale=[0.25, 0.75, 0.25],
                   )
    graph.add_node("right_upper_leg",
                   attach_to="right_leg",
                   mesh=cube,
                   color=[0, 0, 1],
                   position=[0.2, -0.85, 0],
                   rotation=[0, 0, 0.15],
                   scale=[0.25, 0.75, 0.25],
                   )
    graph.add_node("left_lower_leg",
                   attach_to="left_leg",
                   mesh=cube,
                   color=[0.5, 0, 1],
                   position=[-0.25, -1.5, 0],
                   scale=[0.2, 0.75, 0.2],
                   )
    graph.add_node("right_lower_leg",
                   attach_to="right_leg",
                   mesh=cube,
                   color=[0.5, 0, 1],
                   position=[0.25, -1.5, 0],
                   scale=[0.2, 0.75, 0.2],
                   )

    def update(dt):
        # el tiempo
        controller.program_state["total_time"] += dt
        time = controller.program_state["total_time"]

        # control de la camara
        if controller.is_key_pressed(pyglet.window.key.A):
            camera.phi -= dt
        if controller.is_key_pressed(pyglet.window.key.D):
            camera.phi += dt
        if controller.is_key_pressed(pyglet.window.key.W):
            camera.theta -= dt
        if controller.is_key_pressed(pyglet.window.key.S):
            camera.theta += dt
        if controller.is_key_pressed(pyglet.window.key.Q):
            camera.distance += dt
        if controller.is_key_pressed(pyglet.window.key.E):
            camera.distance -= dt
        if controller.is_key_pressed(pyglet.window.key._1):
            camera.type = "perspective"
        if controller.is_key_pressed(pyglet.window.key._2):
            camera.type = "orthographic"

        # actualizacion del monito
        limb_rotation = np.sin(time * 5) / 2
        graph["left_arm"]["transform"] = tr.translate(
            0, 0.5, 0) @ tr.rotationX(limb_rotation) @ tr.translate(0, -0.5, 0)
        graph["right_arm"]["transform"] = tr.translate(
            0, 0.5, 0) @ tr.rotationX(-limb_rotation) @ tr.translate(0, -0.5, 0)
        graph["left_leg"]["transform"] = tr.translate(
            0, -0.5, 0) @ tr.rotationX(-limb_rotation) @ tr.translate(0, 0.5, 0)
        graph["right_leg"]["transform"] = tr.translate(
            0, -0.5, 0) @ tr.rotationX(limb_rotation) @ tr.translate(0, 0.5, 0)

        lower_limb_rotation = np.cos(time * 5) / 3
        graph["left_lower_leg"]["transform"] = tr.translate(
            0, -1.125, 0) @ tr.rotationX(lower_limb_rotation + 0.25) @ tr.translate(0, 1.125, 0)
        graph["right_lower_leg"]["transform"] = tr.translate(
            0, -1.125, 0) @ tr.rotationX(lower_limb_rotation + 0.25) @ tr.translate(0, 1.125, 0)

        camera.update()

    @controller.event
    def on_resize(width, height):
        camera.resize(width, height)

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()

        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
