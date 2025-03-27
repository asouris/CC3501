# importamos las librerias
import pyglet
from OpenGL import GL
import numpy as np
import transformations as tr

# Opcionalmente seteamos variables para el tamaño
WIDTH = 640
HEIGHT = 640
TIME = 0

# controlador de la ventana, basicamente una ventana
class Controller(pyglet.window.Window):
    #Función init se ejecuta al construir el objeto
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)

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
    controller = Controller("Auxiliar 0", width=WIDTH,
                            height=HEIGHT, resizable=True)

    vertex_source_code_img = """
        #version 330

        in vec2 position;
        in vec3 color;
        in float intensity;

        out vec3 fragColor;
        out float fragIntensity;

        void main()
        {
            fragColor = color;
            fragIntensity = intensity;
            gl_Position = vec4(position, 0.0f, 1.0f);
        }
    """           
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
    vert_shader_img = pyglet.graphics.shader.Shader(vertex_source_code_img, "vertex")
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")
    
    # Creación del pipeline
    pipelineimg = pyglet.graphics.shader.ShaderProgram(vert_shader_img, frag_shader)
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Posición de los vértices 
    # 3 vértices con 3 coordenadas (x, y,z)
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

    # Definimos la imagen, con su tamaño y su posicion
    calle = Image("calle.jpg", HEIGHT, WIDTH, 0, HEIGHT - WIDTH)

    transform = tr.identity() 
    # Esta función se llama más abajo
    def update(dt):
        global TIME
        TIME += dt*5
        global transform
        # Incrementamos el ángulo de rotación
        angle = np.radians(50) * dt  # 30 grados por segundo
        # Aplicamos transformación de rotación
        transform = tr.rotationX(angle) @ transform

    @controller.event
    def on_draw():
        global transform
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)

        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipelineimg.use()

        # Dibujamos la imagen
        calle.draw()

        #Cambiamos al pipeline que incluye las transformaciones
        pipeline.use()

        #Transformaciones 
        transform_flat = np.reshape(transform, (16, 1), order="F")
        pipeline["transform"] = transform_flat

        gpu_triangle.draw(GL.GL_TRIANGLES)

    # Como dice la documentación:
    # The schedule_interval method causes a function to be called every “n” seconds: 
    # schedule_interval(function, n)
    pyglet.clock.schedule_interval(update, 1/60)

    # Esta función recibe opcionalmente la frecuencia en que se actualiza la pantalla
    # por defecto es 1/60 pero podrían cambiarla: pyglet.app.run(1/120)
    pyglet.app.run()