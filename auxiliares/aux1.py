import pyglet
from OpenGL import GL
import numpy as np

WIDTH = 640
HEIGHT = 640

# controlador de la ventana


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)

    def update(self, dt):
        pass


# programa principal
if __name__ == "__main__":
    # creamos una instancia del controlador
    controller = Controller("Auxiliar 1", width=WIDTH,
                            height=HEIGHT, resizable=True)

    vertex_source_code = """
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

    # Código del fragment shader
    # La salida es un vector de 4 componentes (r, g, b, a)
    # donde a es la transparencia (por ahora no nos importa, se deja en 1)
    # El color resultante de cada fragmento ("pixel") es el color del vértice multiplicado por su intensidad
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

    # Posición de los vértices de un triángulo
    # 3 vértices con 2 coordenadas (x, y)
    # donde (0, 0) es el centro de la pantalla
    positions = np.array([
        -0.5, -0.5,
        0.5, -0.5,
        0.0,  0.5
    ], dtype=np.float32)

    # Colores de los vértices del triángulo
    # 3 vértices con 3 componentes (r, g, b)
    colors = np.array([
        1, 0, 0,
        0, 1, 0,
        0, 0, 1
    ], dtype=np.float32)

    # Intensidad de los vértices del triángulo
    # 3 vértices con 1 componente (intensidad)
    intensities = np.array([
        1, 0.5, 0
    ], dtype=np.float32)

    gpu_triangle = pipeline.vertex_list(3, GL.GL_TRIANGLES)
    gpu_triangle.position = positions
    gpu_triangle.color = colors
    gpu_triangle.intensity = intensities

    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()

        gpu_triangle.draw(GL.GL_TRIANGLES)

    pyglet.clock.schedule_interval(controller.update, 1/60)
    pyglet.app.run()
