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

# Definimos la clase "Imagen" para generar imagenes mas facilmente
class Image():
    def __init__(self, path, width, height, x = 0, y = 0):
        self.image = pyglet.resource.image(path)
        self.image.width = width
        self.image.height = height
        self.x = x
        self.y = y

    def draw(self):
        self.image.blit(self.x, self.y)

# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Auxiliar", width=WIDTH,
                            height=HEIGHT, resizable=True)


    # A continuación se encuentra el vertex shader          
    vertex_source_code = """
        #version 330

        in vec3 position;
        in vec3 color;
        in float intensity;
        uniform mat4 transform;

        uniform vec3 u_color = vec3(1.0);

        out vec3 fragColor;
        out float fragIntensity;

        void main()
        {
            fragColor = u_color;
            fragIntensity = intensity;
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

    vaca = mesh_from_file(root + "/assets/cow.obj")[0]['mesh']
    vaca.init_gpu_data(pipeline)


    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)

        # si hay algo dibujado se limpia del frame
        controller.clear()
        
        pipeline.use()

        vacaTransform = pyglet.math.Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90) @ tr.translate(0, 0, -2)
        pipeline["transform"] = np.reshape(vacaTransform, (16,1), order="F")
        pipeline["u_color"] = np.array([1, 0, 1], dtype=np.float32)

        # Dibujamos la imagen
        vaca.draw(GL.GL_TRIANGLES)


    #pyglet.clock.schedule_interval(update, 1/60)
    
    # Esta función recibe opcionalmente la frecuencia en que se actualiza la pantalla
    # por defecto es 1/60 pero podrían cambiarla: pyglet.app.run(1/120)
    pyglet.app.run()
