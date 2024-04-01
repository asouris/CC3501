import pyglet
import numpy as np
import os
import trimesh as tm
from OpenGL import GL
from pathlib import Path
from utils.helpers import Model, Mesh

WIDTH = 640
HEIGHT = 640
TIME = 0

# controlador de la ventana


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)

        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)

    def update(self, dt):
        pass


# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Blender clouds moving", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Importamos los shaders
    with open(Path(os.path.dirname(__file__)) / "shaders/transform_alpha.vert") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/color_alpha.frag") as f:
        fragment_source_code = f.read()

    # Compilación de shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")
    # Creación del pipeline
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Creamos nuestras figuras

    # importamos cloud desde un archivo obj que obtuve de blender
    # Cloud inicia en el centro de la pantalla
    cloud = Mesh(Path(os.path.dirname(__file__)) /
                 'assets/cloud.obj', 1, [1, 1, 1])
    cloud.init_gpu_data(pipeline)
    cloud.scale = np.array([0.2, 0.2, 0.2], dtype=np.float32)

    # Cloud2 inicia un poquito arriba y hacia la derecha
    cloud2 = Mesh(Path(os.path.dirname(__file__)) /
                  'assets/cloud.obj', 1, [1, 1, 1])
    cloud2.init_gpu_data(pipeline)
    cloud2.position += [0.7, 0.3, 0]
    cloud2.scale = np.array([0.2, 0.2, 0.2], dtype=np.float32)

    # Cloud3 inicia un poquito arriba pero hacia la izquierda
    cloud3 = Mesh(Path(os.path.dirname(__file__)) /
                  'assets/cloud.obj', 1, [1, 1, 1])
    cloud3.init_gpu_data(pipeline)
    cloud3.position += [-0.8, 0.2, 0]
    cloud3.scale = np.array([0.2, 0.2, 0.2], dtype=np.float32)

    def update(dt):
        global TIME
        TIME += dt

        # cloud avanza un tercio de dt en cada frame hasta que llega a 1.5 y se devuelve
        cloud.position[0] = cloud.position[0] + \
            dt/3 if abs(cloud.position[0] < 1.5) else -1.5
        # cloud2 avanza un cuarto de dt en cada frame hasta 1.5 y vuelve
        cloud2.position[0] = cloud2.position[0] + \
            dt/4 if abs(cloud2.position[0] < 1.5) else -1.5
        # cloud3 avanza un 3.5 de dt en cada frame hasta 1.5 y vuelve
        cloud3.position[0] = cloud3.position[0] + \
            dt/3.5 if abs(cloud3.position[0] < 1.5) else -1.5

    @controller.event
    def on_draw():
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(145/255, 220/255, 235/255, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        # Por cada figura hacemos dos cosas:
        # le pasamos la transformacion de la figura al vertex shader
        pipeline["u_model"] = cloud.get_transform()
        cloud.draw()  # y dibujamos

        pipeline["u_model"] = cloud2.get_transform()
        cloud2.draw()

        pipeline["u_model"] = cloud3.get_transform()
        cloud3.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
