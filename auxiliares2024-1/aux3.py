import pyglet
import numpy as np
import os
import trimesh as tm
from OpenGL import GL
from pathlib import Path
from utils.helpers import Model, Mesh
import utils.shapes as shapes

WIDTH = 640
HEIGHT = 640
TIME = 0

# Variables body_v, background_color
body_v = 0
background_color = [1, 1, 1]  # blanco

# Controlador de la ventana


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)

        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)

        # Para recibir los input aqui
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)

    # Para checkear las teclas presionadas
    # funcion is_key_pressed()
    def is_key_pressed(self, key):
        return self.key_handler[key]

    def update(self, dt):
        pass


# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Aux 03", width=WIDTH,
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
    # En este caso un body que voy a controlar
    # Será un capsule, y sera rojo
    body = Model(shapes.Capsule['position'], [
                 1, 0, 0]*24, 1.0, shapes.Capsule['indices'])
    body.init_gpu_data(pipeline)

    # le hacemos scale a 0.1

    body.scale = [0.1, 0.1, 1]

    def update(dt):
        global TIME
        global body_v
        TIME += dt

        # controles para A y D (izquierda y derecha)
        if controller.is_key_pressed(pyglet.window.key.A):
            body.position[0] -= dt
            print("alo")

        if controller.is_key_pressed(pyglet.window.key.D):
            body.position[0] += dt

        # Luego control para W, para el salto
        if controller.is_key_pressed(pyglet.window.key.W) and body.position[1] == 0.0:
            body_v = 0.05
        # Actualizamos la posicion dad la velocidad
        body.position[1] += body_v
        # Mientras sea mayor a 0, puedo caer (disminuimos la velocidad gradualmente)
        if body.position[1] > 0:
            body_v -= dt/4
        else:
            body.position[1] = 0.0
            body_v = 0

    # Quiero controlar el color de fondo con mi scroll

    @controller.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        global background_color

        # Dado que lo definí mas arriba, puedo setearlo le voy a sumar 1/8
        # de mi scroll en y a cada valor del color

        background_color[0] += scroll_y/8
        background_color[1] += scroll_y/8
        background_color[2] += scroll_y/8

    @controller.event
    def on_draw():
        global background_color
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # color de fondo al limpiar un frame (0,0,0) es negro
        # acá hay que cambiar algo para poder incluir el input
        GL.glClearColor(
            background_color[0], background_color[1], background_color[2], 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        # Por cada figura hacemos dos cosas:
        # le pasamos la transformacion de la figura al vertex shader
        # y luego lo dibujamos
        pipeline["u_transform"] = body.get_transform()
        body.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
