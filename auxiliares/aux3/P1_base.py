# LIBRERIAS externas
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import clock

import sys, os
import numpy as np
# la siguiente linea le dice a python que cuando busque librerías, busque en la carpeta actual
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))

# MÓDULOS HECHOS POR EQUIPO DOCENTE (cuidado con las rutas)
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model

from collections import deque
from itertools import chain

# Controla la ventana y el paso del tiempo
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.width = 600
        self.height = 600

        self.time = 0

# Definimos un objeto partícula
class Particle(object):
    def __init__(self, position):
        ???

    def step(self, dt):
        ???


if __name__ == "__main__":

    controller = Controller(800, 800, "Auxiliar 2")

    vert_source = """
    #version 330

    in vec3 position;

    void main()
    {
        gl_PointSize = ???;
        gl_Position = vec4(position, 1.0);
    }
    """
    frag_source = """
    #version 330

    out vec4 outColor;

    void main()
    {
        outColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
    """

    # Definimos el pipeline usando los shaders
    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))
    
    # Esta variable almacena el camino a la carpeta actual
    root = os.path.dirname(__file__)


    @controller.event
    def on_draw():
        controller.clear()

        # Limpia pantalla y la coloca en el color [1, 1, 1, 1] = blanco
        glClearColor(0,0,0,1)

        # usaremos esto en el shader, porque dibujaremos GL_POINTS
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        pipeline.use()


    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        # convertimos las coordenadas de la pantalla
        # (que fueron calculadas en la etapa de SCREEN MAPPING)
        # a coordenadas del volumen normalizado: entre -1 y 1
        norm_screen_x = (x / controller.width) * 2 - 1
        norm_screen_y = (y / controller.height) * 2 - 1
        
        result = [norm_screen_x, norm_screen_y, 0.0, 1.0]


    def update_particle_system(dt, controller):
        ???

    clock.schedule(update_particle_system, controller)
    run()