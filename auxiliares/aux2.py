import pyglet
from OpenGL import GL
import numpy as np
import utils.shapes as shapes
import utils.transformations as tr
import os

from pathlib import Path

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

# Clase Model que va a ocuparse de configurar nuestras figuras


class Model():
    def __init__(self, position_data, color_data, index_data=None):
        self.position_data = position_data
        self.color_data = color_data

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        self.scale = np.array([1, 1, 1], dtype=np.float32)

    # Genera el vertex list y le asigna las posiciones y los colores

    def init_gpu_data(self, pipeline):
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(
                len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(
                len(self.position_data) // 3, GL.GL_TRIANGLES)

        self.gpu_data.position[:] = self.position_data
        self.gpu_data.color[:] = self.color_data

    # Simplemente dibuja

    def draw(self, mode=GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)

    # Genera la matriz con todas las transformaciones

    def get_transform(self):
        translation_matrix = tr.translate(
            self.position[0], self.position[1], self.position[2])
        rotation_matrix = tr.rotationX(
            self.rotation[0]) @ tr.rotationY(self.rotation[1]) @ tr.rotationZ(self.rotation[2])
        scale_matrix = tr.scale(self.scale[0], self.scale[1], self.scale[2])
        transformation = translation_matrix @ rotation_matrix @ scale_matrix
        return np.reshape(transformation, (16, 1), order="F")


# Programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Auxiliar 2", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Importamos los shaders
    with open(Path(os.path.dirname(__file__)) / "shaders/transform.vert") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "shaders/color.frag") as f:
        fragment_source_code = f.read()

    # Compilación de shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")
    # Creación del pipeline
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    capsule = Model(
        shapes.Capsule["position"], shapes.Capsule["color"], shapes.Capsule['indices'])
    capsule.init_gpu_data(pipeline)
    capsule.scale = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    capsule.position = np.array([-0.5, 0.5, 0], dtype=np.float32)

    triangle = Model(shapes.Triangle["position"], shapes.Triangle["color"])
    triangle.init_gpu_data(pipeline)
    triangle.scale = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    triangle.position = np.array([0.5, 0.5, 0], dtype=np.float32)

    triangle2 = Model(shapes.Triangle["position"], shapes.Triangle["color"])
    triangle2.init_gpu_data(pipeline)
    triangle2.scale = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    triangle2.position = np.array([0, -0.5, 0], dtype=np.float32)

    def update(dt):
        global TIME
        TIME += dt
        triangle.rotation[2] += dt
        capsule.rotation[1] += dt
        triangle2.position[0] = np.sin(TIME)

    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        pipeline["u_transform"] = capsule.get_transform()
        capsule.draw()

        pipeline["u_transform"] = triangle.get_transform()
        triangle.draw()

        pipeline["u_transform"] = triangle2.get_transform()
        triangle2.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
