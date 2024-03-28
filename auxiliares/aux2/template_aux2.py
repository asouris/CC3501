import pyglet
from OpenGL import GL
import numpy as np
import utils.shapes as shapes
import utils.transformations as tr
import os
# import sys
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

    def init_gpu_data(self, pipeline):
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(
                len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(
                len(self.position_data) // 3, GL.GL_TRIANGLES)

        self.gpu_data.position[:] = self.position_data
        self.gpu_data.color[:] = self.color_data

    def draw(self, mode=GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)

    def get_transform(self):
        translation_matrix = tr.translate(
            self.position[0], self.position[1], self.position[2])
        rotation_matrix = tr.rotationX(
            self.rotation[0]) @ tr.rotationY(self.rotation[1]) @ tr.rotationZ(self.rotation[2])
        scale_matrix = tr.scale(self.scale[0], self.scale[1], self.scale[2])
        transformation = translation_matrix @ rotation_matrix @ scale_matrix
        return np.reshape(transformation, (16, 1), order="F")


# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Auxiliar 1", width=WIDTH,
                            height=HEIGHT, resizable=True)

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

    positions_body = [
        1, 1, 0.0,
        -1, 1, 0.0,
        0, 2, 0.0,
        0, -6, 0.0,
        0.5, 2.5, 0.0,
        -0.5, 2.5, 0.0,
        2, 5, 0.0,
        -2, 5, 0.0,
        1, 6, 0.0,
        -1, 6, 0.0
    ]

    colors_body = [88/255, 57/255, 39/255] * 10
    intensities_body = [1]*10

    body_index = [
        2, 0, 3,
        2, 1, 3,
        4, 6, 8,
        5, 7, 9
    ]

    positions_wings = [
        1, 1, 0.0,
        -1, 1, 0.0,
        3, 3, 0.0,
        8, 5, 0.0,
        7, 0, 0.0,
        6, 0, 0.0,
        7, -2, 0.0,
        5, -5, 0.0,
        3, -5, 0.0,
        0, -3, 0.0,
        -3, -5, 0.0,
        -5, -5, 0.0,
        -7, -2, 0.0,
        -6, 0, 0.0,
        -7, 0, 0.0,
        -8, 5, 0.0,
        -3, 3, 0.0
    ]

    colors_wings = [
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        194/255, 53/255, 219/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        1, 192/255, 203/255,
        194/255, 53/255, 219/255,
        1, 192/255, 203/255
    ]
    intensities_wings = [1]*17

    wings_index = [
        0, 9, 5,
        5, 0, 2,
        2, 5, 3,
        3, 4, 5,
        9, 8, 7,
        9, 7, 5,
        5, 6, 7
    ]
    wing2_index = [
        9, 10, 11,
        11, 13, 9,
        11, 13, 12,
        14, 13, 15,
        15, 16, 13,
        13, 16, 1,
        1, 9, 13
    ]

    body = Model(positions_body, colors_body, body_index)
    body.init_gpu_data(pipeline)
    body.scale = np.array([1/12, 1/12, 1/12], dtype=np.float32)

    body.rotation[2] = -(np.pi/2-np.pi/10)
    # body.rotation[0] = np.pi/4

    body.position[0] = -1

    wing1 = Model(positions_wings, colors_wings, wings_index)
    wing1.init_gpu_data(pipeline)
    wing1.scale = np.array([1/12, 1/12, 1/12], dtype=np.float32)

    wing1.rotation[2] = -np.pi/2 - np.pi/10
    # wing1.rotation[1] = np.pi/12
    wing1.rotation[0] = np.pi

    wing1.position[0] = -1

    wing2 = Model(positions_wings, colors_wings, wing2_index)
    wing2.init_gpu_data(pipeline)
    wing2.scale = np.array([1/12, 1/12, 1/12], dtype=np.float32)

    wing2.rotation[2] = -np.pi/2 + np.pi/10
    # wing2.rotation[1] = np.pi/12

    wing2.position[0] = -1

    axes = Model(shapes.Axes["position"], shapes.Axes["color"])
    axes.init_gpu_data(pipeline)

    """capsule = Model(
        shapes.Capsule["position"], shapes.Capsule["color"], shapes.Capsule['indices'])
    capsule.init_gpu_data(pipeline)
    # capsule.position = np.array([0.6, 0.5, 0], dtype=np.float32)

    triangle = Model(shapes.Triangle["position"], shapes.Triangle["color"])
    triangle.init_gpu_data(pipeline)
    """
    def update(dt):
        global TIME
        TIME += dt
        body.position[1] = np.sin(TIME*2)/(TIME) + 0.01
        wing1.position[1] = np.sin(TIME*2)/(TIME)
        wing2.position[1] = np.sin(TIME*2)/(TIME)

        # body.position[0] += 0.003
        # wing1.position[0] += 0.003
        # wing2.position[0] += 0.003

        body.scale -= 0.0001
        wing1.scale -= 0.0001
        wing2.scale -= 0.0001

        wing2.rotation[0] = np.sin(4*TIME+0.3)*0.7 + np.pi/4
        wing1.rotation[0] = np.sin(4*TIME)*0.7 - (3*np.pi)/4

    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(145/255, 220/255, 235/255, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        pipeline["u_model"] = axes.get_transform()
        axes.draw(GL.GL_LINES)

        pipeline["u_model"] = wing1.get_transform()
        wing1.draw(GL.GL_TRIANGLES)

        pipeline["u_model"] = body.get_transform()
        body.draw(GL.GL_TRIANGLES)

        pipeline["u_model"] = wing2.get_transform()
        wing2.draw(GL.GL_TRIANGLES)

        # pipeline["u_model"] = capsule.get_transform()
        # capsule.draw()

        # pipeline["u_model"] = triangle.get_transform()
        # triangle.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
