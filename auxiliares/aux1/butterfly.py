import pyglet           # pip install pyglet
from OpenGL import GL   # pip install PyOpenGL
import numpy as np      # pip install numpy o conda install numpy

WIDTH = 640
HEIGHT = 640


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        # Evita error cuando se redimensiona a 0
        self.set_minimum_size(240, 240)
        self.set_caption(title)

    def update(self, dt):
        pass


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Auxiliar 1", width=WIDTH,
                            height=HEIGHT, resizable=True)

    # Código del vertex shader
    # cada vértice tiene 3 atributos
    # posición (x, y)
    # color (r, g, b)
    # intensidad
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

    positions_body = np.array([
        1, 1,
        -1, 1,
        0, 2,
        0, -6,
        0.5, 2.5,
        -0.5, 2.5,
        2, 5,
        -2, 5,
        1, 6,
        -1, 6
    ], dtype=np.float32)

    positions_body *= 1/12

    colors_body = np.array([88/255, 57/255, 39/255] * 10, dtype=np.float32)
    intensities_body = np.array([1]*10, dtype=np.float32)

    body_index = np.array([
        2, 0, 3,
        2, 1, 3,
        4, 6, 8,
        5, 7, 9
    ], dtype=np.uint32)

    positions_wings = np.array([
        1, 1,  # 1
        -1, 1,  # 3
        3, 3,  # 4
        8, 5,
        7, 0,
        6, 0,
        7, -2,
        5, -5,
        3, -5,
        0, -3,
        -3, -5,  # 12
        -5, -5,
        -7, -2,
        -6, 0,
        -7, 0,
        -8, 5,
        -3, 3
    ], dtype=np.float32)

    positions_wings *= 1/12

    colors_wings = np.array([1, 192/255, 203/255]*17, dtype=np.float32)
    intensities_wings = np.array([1]*17, dtype=np.float32)

    wings_index = np.array([
        0, 9, 5,
        5, 0, 2,
        2, 5, 3,
        3, 4, 5,
        9, 8, 7,
        9, 7, 5,
        5, 6, 7,
        9, 10, 11,
        11, 13, 9,
        11, 13, 12,
        14, 13, 15,
        15, 16, 13,
        13, 16, 1,
        1, 9, 13
    ], dtype=np.uint32)

    body = pipeline.vertex_list_indexed(10, GL.GL_TRIANGLES, body_index)
    body.position = positions_body
    body.color = colors_body
    body.intensity = intensities_body

    wings = pipeline.vertex_list_indexed(17, GL.GL_TRIANGLES, wings_index)
    wings.position = positions_wings
    wings.color = colors_wings
    wings.intensity = intensities_wings

    @controller.event
    def on_draw():
        GL.glClearColor(1, 1, 1, 1.0)
        controller.clear()
        pipeline.use()

        wings.draw(GL.GL_TRIANGLES)
        body.draw(GL.GL_TRIANGLES)

    # se ejecuta update del controller cada 1/60 segundos
    pyglet.clock.schedule_interval(controller.update, 1/60)
    pyglet.app.run()  # se ejecuta pyglet
