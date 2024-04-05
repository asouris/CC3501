import pyglet
import numpy as np
import os
import trimesh as tm
from OpenGL import GL
from pathlib import Path
from utils.helpers import Model, Mesh

# :)

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
    controller = Controller("Amongus Transparent", width=WIDTH,
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

    # Importamos varios amongus
    # este sus está en el z = 0.3 (atras)
    sus1 = Mesh(Path(os.path.dirname(__file__)) / 'assets/amongus.obj',
                1, [187/255, 34/255, 230/255])  # morado
    sus1.init_gpu_data(pipeline)
    sus1.scale = [0.6, 0.6, 1]
    sus1.position = [0, 0, 0.3]

    # este sus está en el z = 0.2
    sus2 = Mesh(Path(os.path.dirname(__file__)) /
                'assets/amongus.obj', 0.8, [88/255, 235/255, 59/255])  # verde
    sus2.init_gpu_data(pipeline)
    sus2.scale = [0.3, 0.3, 1]
    sus2.position = [0.5, 0.5, 0.2]

    # este sus está en el z = 0.1
    sus3 = Mesh(Path(os.path.dirname(__file__)) /
                'assets/amongus.obj', 0.5,  [230/255, 147/255, 46/255])  # naranja
    sus3.init_gpu_data(pipeline)
    sus3.scale = [0.3, 0.3, 1]
    sus3.position = [-0.5, -0.5, 0.1]

    # este sus está en el z = 0 (delante)
    sus4 = Mesh(Path(os.path.dirname(__file__)) /
                'assets/amongus.obj', 0.3, [75/255, 70/255, 224/255])  # azul
    sus4.init_gpu_data(pipeline)
    sus4.scale = [0.3, 0.3, 1]
    sus4.position = [0.5, -0.5, 0]

    def update(dt):
        global TIME
        TIME += dt

        # escaleo de los sus
        sus1.scale = [abs(np.sin(TIME)*1/2), abs(np.sin(TIME)*1/2), 1]
        sus2.scale = [np.cos(TIME)*0.5 + 1, np.cos(TIME)*0.5 + 1, 1]
        sus3.scale = [abs(np.cos(TIME)*1/2), abs(np.cos(TIME)*1/2), 1]
        sus4.scale = [np.sin(TIME)*0.5 + 1, np.sin(TIME)*0.5 + 1, 1]

    @controller.event
    def on_draw():

        # Lineas para activar el uso del parámetro alpha
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(1, 1, 1, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        # Por cada figura hacemos dos cosas:
        # le pasamos la transformacion de la figura al vertex shader
        pipeline["u_transform"] = sus1.get_transform()
        sus1.draw()  # y dibujamos

        pipeline["u_transform"] = sus2.get_transform()
        sus2.draw()

        pipeline["u_transform"] = sus3.get_transform()
        sus3.draw()

        pipeline["u_transform"] = sus4.get_transform()
        sus4.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
