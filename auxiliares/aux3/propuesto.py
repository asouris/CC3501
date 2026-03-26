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

import random

# Controla la ventana y el paso del tiempo
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.width = 800
        self.height = 800

        self.time = 0
        self.particles = deque()
        self.particles_gpu_object = None

# Definimos un objeto partícula
class Particle(object):
    def __init__(self, position, ttl):
        self.position = np.array(position, dtype=np.float32)
        # por simpleza asumiremos que tiene velocidad constante en el eje y, sin aceleraci[on]

        random_x = random.randint(-2, 2)
        random_y = random.randint(-2, 2)

        self.velocity = np.array([random_x, random_y, 0], dtype=np.float32)
        # ttl es la abreviación de "time to live", es el tiempo de vida restante
        self.ttl = ttl

    def step(self, dt):
        # en cada paso de la simulación pasan dos cosas.
        # por un lado, se reduce el tiempo de vida de la partícula
        self.ttl = self.ttl - dt
        # por otro, debemos actualizar su posición
        # en este caso sabemos que la velocidad siempre apunta en la misma dirección
        # pero en una aplicación más avanzada hay que calcular la velocidad
        # usamos el método de Euler
    
        self.velocity = self.velocity + [0, -.05, 0]
        self.position = self.position + dt * self.velocity

    def alive(self):
        # esta función utilitaria nos dice si la partícula está viva
        return bool(self.ttl > 0)


if __name__ == "__main__":

    controller = Controller(800, 800, "Auxiliar")

    vert_source = """
    #version 330

    in vec3 position;
    in float ttl;
    out float alpha;

    void main()
    {
        gl_PointSize = 15.0 * (ttl / 3.0);
        gl_Position = vec4(position, 1.0);
        alpha = ttl / 3.0;
    }
    """
    frag_source = """
    #version 330

    in float alpha;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(1.0, 1.0, 1.0, alpha);
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

        # si no tenemos partículas, no dibujamos
        if controller.particles_gpu_object is not None:
            controller.particles_gpu_object.draw(GL_POINTS)

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        # convertimos las coordenadas de la pantalla
        # (que fueron calculadas en la etapa de SCREEN MAPPING)
        # a coordenadas del volumen normalizado: entre -1 y 1
        norm_screen_x = (x / controller.width) * 2 - 1
        norm_screen_y = (y / controller.height) * 2 - 1
        
        result = [norm_screen_x, norm_screen_y, 0.0, 1.0]

        # y el resultado se lo asignamos a una partícula
        controller.particles.append(Particle((result[0], result[1], 0.0), 3))

    def update_particle_system(dt, controller):

        # primero debemos revisar cuales partículas ya no están vivas
        to_remove = 0
        for i in range(len(controller.particles)):
            p = controller.particles[i]
            p.step(dt)

            if not p.alive():
                to_remove += 1

        # descartamos a las que dejaron de vivir
        for i in range(to_remove):
            controller.particles.popleft()

        if controller.particles_gpu_object is not None:
            controller.particles_gpu_object.delete()
            controller.particles_gpu_object = None

        # si hay partículas vivas, hay que copiarlas a la GPU
        if len(controller.particles) > 0:
            controller.particles_gpu_object = pipeline.vertex_list( len(controller.particles), GL_POINTS )
            
            pos = []
            ttls = []
            for p in controller.particles:
                pos += p.position.tolist()
                ttls.append(p.ttl)

            controller.particles_gpu_object.position[:] = np.array(pos)
            controller.particles_gpu_object.ttl[:] = np.array(ttls)

    clock.schedule(update_particle_system, controller)
    run()