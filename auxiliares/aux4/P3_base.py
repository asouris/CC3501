# importamos las librerias
import pyglet
from OpenGL import GL
import numpy as np

import os
import sys

# Para facilitar el uso de módulos, obtenemos el camino a la raiz del repositorio (CC3501)
root = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))
# Y añadimos este camino a sys.path. De esta forma python sabe donde buscar
sys.path.append(root)

import grafica.transformations as tr
from utils.helpers import mesh_from_file

# Opcionalmente seteamos variables para el tamaño
WIDTH = 640
HEIGHT = 640

# controlador de la ventana, basicamente una ventana
class Controller(pyglet.window.Window):
    #Función init se ejecuta al construir el objeto
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.time = 0.0
        self.car_transform = tr.identity()

# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Auxiliar", width=WIDTH,
                            height=HEIGHT, resizable=True)


    # A continuación se encuentra el vertex shader          
    vertex_source_code = """
        #version 330

        in vec3 position;
        uniform mat4 transform;
        
        //¿como pasamos el color???

        out vec3 fragColor;

        void main()
        {
            fragColor = ???;
            gl_Position = transform * vec4(position, 1.0f);
        }
    """

    # Código del fragment shader
    fragment_source_code = """
        #version 330

        in vec3 fragColor;
        out vec4 outColor;

        void main()
        {
            outColor = vec4(fragColor, 1.0f);
        }
    """

    # Compilación de shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")
    
    # Creación del pipeline
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # hay que importar los vertices :0


    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)

        # si hay algo dibujado se limpia del frame
        controller.clear()
        
        pipeline.use()

        # hay que pasar los uniforms y dibujar el objeto
    
    # Esta función recibe opcionalmente la frecuencia en que se actualiza la pantalla
    # por defecto es 1/60 pero podrían cambiarla: pyglet.app.run(1/120)
    pyglet.app.run()
