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

        out vec3 fragColor;
        out float fragIntensity;

        void main()
        {
            fragColor = color;
            fragIntensity = intensity;
            gl_Position = transform * vec4(position, 1.0f);
        }
    """

    # Código del fragment shader
    fragment_source_code = """
        #version 330

        in vec3 fragColor;
        in float fragIntensity;
        out vec4 outColor;

        void main()
        {
            outColor = fragIntensity * vec4(fragColor, 1.0f);
        }
    """

    # Compilación de shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")
    
    # Creación del pipeline
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Posición de los vértices 
    # 3 vértices con 3 coordenadas (x, y, z)
    # donde (0, 0, 0) es el centro de la pantalla
    positions = np.array([
        #Auto
        -0.2, -0.3, 0.0,
        0.2, -0.3, 0.0,
        0.2,  0.3, 0.0,
        -0.2,  0.3, 0.0, 
        #Vidrio
        -0.15, 0.1, 0.0,
        0.15, 0.1, 0.0,
        0.15,  0.2, 0.0,
        -0.15,  0.2, 0.0,
        #Luces
        -0.2, 0.3, 0.0,
        -0.1, 0.3, 0.0,
        -0.1,  0.25, 0.0,
        -0.2,  0.25, 0.0,
        0.2, 0.3, 0.0,
        0.1, 0.3, 0.0,
        0.1,  0.25, 0.0,
        0.2,  0.25, 0.0,
    ], dtype=np.float32)

    index = np.array([
         0, 1, 2, 
         2, 3, 0,
         4, 5, 6,
         6, 7, 4,
         8, 9, 10,
         10, 11, 8,
         12, 13, 14,
         14, 15, 12
    ], dtype=np.uint32)

    # Colores de los vértices del triángulo
    # 3 vértices con 3 componentes (r, g, b)
    colors = np.array([
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        168/255, 235/255, 242/255,
        168/255, 235/255, 242/255,
        168/255, 235/255, 242/255,
        168/255, 235/255, 242/255,
        1, 1, 1,
        1, 1, 1,
        1, 1, 1,
        1, 1, 1,
        1, 1, 1,
        1, 1, 1,
        1, 1, 1,
        1, 1, 1
    ], dtype=np.float32)

    # Intensidad de los vértices del triángulo
    # 3 vértices con 1 componente (intensidad)
    intensities = np.array([
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
    ], dtype=np.float32)

    # Ahora asignamos lo que definimos a la figura:
    # Aquí prueben cambiar GL_TRIANGLES por GL_LINE_LOOP
    gpu_triangle = pipeline.vertex_list_indexed(16, GL.GL_TRIANGLES, index)
    gpu_triangle.position = positions
    gpu_triangle.color = color= colors
    gpu_triangle.intensity = intensities

    position_calle = np.array([
        -1, 1, 0,
        -1, 0.3, 0,
        -1, -0.3, 0,
        -1, -1, 0,
        -0.3, -1, 0, #4
        0.3, -1, 0,
        1, -1, 0,
        1, -0.3, 0,
        1, 0.3, 0,   #8
        1, 1, 0,
        0.3, 1, 0,
        -0.3, 1, 0,
        -0.3, 0.3, 0,  #12
        -0.3, -0.3, 0,
        0.3, -0.3, 0,
        0.3, 0.3, 0,    #15
        -1, 0.3, 0,
        -1, -0.3, 0,
        -0.3, -1, 0,    #18
        0.3, -1, 0,
        1, -0.3, 0,
        1, 0.3, 0,      #21
        0.3, 1, 0,
        -0.3, 1, 0,
        -0.3, 0.3, 0,   #24
        -0.3, -0.3, 0,
        0.3, -0.3, 0,
        0.3, 0.3, 0,    #27
    ])

    indices_calle = np.array([
        0, 1, 11, 
        11, 1, 12,
        16, 17, 24,
        24, 17, 25,
        2, 3, 13,
        13, 3, 4,
        7, 14, 5,
        7, 5, 6,
        21, 27, 26, 
        21, 26, 20,
        9, 10, 15,
        9, 15, 8,
        22, 23, 18, 
        22, 18, 19
    ])

    colors_calle = np.array([
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,#4
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,   #8
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4, #12
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,
        0.2, 0.8, 0.4,    #15
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
        0.4, 0.4, 0.4,
    ])

    intensities_calle = np.array([1]*28, dtype=np.float32)
    gpu_calle = pipeline.vertex_list_indexed(28, GL.GL_TRIANGLES, indices_calle)
    gpu_calle.position = position_calle
    gpu_calle.color = color= colors_calle
    gpu_calle.intensity = intensities_calle

    def update(dt):
        controller.time += dt*5

        # Incrementamos el ángulo de rotación
        angle = np.radians(50) * controller.time 
        # Aplicamos transformación de rotación
        controller.car_transform = tr.rotationX(angle)


    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)

        # si hay algo dibujado se limpia del frame
        controller.clear()
        
        pipeline.use()

        transform = tr.identity()
        transform = np.reshape(transform, (16, 1), order="F")
        pipeline["transform"] = transform

        # Dibujamos la imagen
        gpu_calle.draw(GL.GL_TRIANGLES)

        transform = np.reshape(controller.car_transform, (16, 1), order="F")
        pipeline["transform"] = transform

        gpu_triangle.draw(GL.GL_TRIANGLES)

    pyglet.clock.schedule_interval(update, 1/60)
    
    # Esta función recibe opcionalmente la frecuencia en que se actualiza la pantalla
    # por defecto es 1/60 pero podrían cambiarla: pyglet.app.run(1/120)
    pyglet.app.run()
