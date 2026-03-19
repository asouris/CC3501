#LIBRERIAS externas
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window
from pyglet.gl import *
from pyglet.app import run

import sys, os
import numpy as np
# la siguiente linea le dice a python que cuando busque librerías, busque en la carpeta actual
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))


# MÓDULOS HECHOS POR EQUIPO DOCENTE (cuidado con las rutas)
from utils.camera import FreeCamera

#Controla la ventana y el paso del tiempo
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0

# Esta clase nos ayuda a simular el comportamiento de una cámara
# Estan invitados a estudiar este código, pero lo veremos con más detención en el futuro...
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 2

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward

if __name__ == "__main__":

    controller = Controller(800,600,"Auxiliar 2")
    controller.set_exclusive_mouse(True)

    vert_source = """
    #version 330

    in vec3 position;
    in vec3 color;

    out vec3 fragColor;
    void main()
        {
            fragColor = color;
            gl_Position = vec4(position, 1.0f);
        }
    """
    frag_source = """
    #version 330

        in vec3 fragColor;
        out vec4 outColor;

        void main()
        {
            outColor = vec4(fragColor, 1.0f);
        }
    """

    # Definimos el pipeline usando los shaders
    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))
    
    # Esta variable almacena el camino a la carpeta actual
    root = os.path.dirname(__file__)

    # Definimos las posiciones de nuestros vértices, son 2 triangulos = 6 vértices
    positions = np.array([
        -0.5, -0.5, 0.0,
        0.5, -0.5, 0.0,
        -0.5,  0.5, 0.0,
        0.5, 0.5, 0.0,
        0.5, -0.5, 0.0,
        -0.5,  0.5, 0.0
    ], dtype=np.float32)

    # Definimos los colores de cada vertice, un color (r, g, b) por cada vertices
    colors = np.array([
        0, 0, 0,
        0, 0, 0,
        0, 0, 0,
        0, 0, 0,
        0, 0, 0,
        0, 0, 0
    ], dtype=np.float32)

    # Acá se define un objeto de GPU, con 6 vertices
    gpu_triangle = pipeline.vertex_list(6, GL_TRIANGLES)

    # Al objeto, le asignamos las posiciones y los colores
    gpu_triangle.position = positions
    gpu_triangle.color = colors

    # Función on_draw() realiza cada render
    @controller.event
    def on_draw():
        controller.clear()

        # Limpia pantalla y la coloca en el color [1, 1, 1, 1] = blanco
        glClearColor(1,1,1,1)

        # Decimos que pipeline vamos a usar
        pipeline.use()
        
        # Le decimos que dibuje el objeto
        gpu_triangle.draw(GL_TRIANGLES)

    run()