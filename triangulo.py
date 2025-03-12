# Código de https://github.com/arielriveros de cuando fue aux

import pyglet
from OpenGL import GL
import numpy as np

WIDTH = 640
HEIGHT = 640
TIME = 0


class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240)
        self.set_caption(title)

    def update(self, dt):
        pass


if __name__ == "__main__":
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

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(
        fragment_source_code, "fragment")

    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    positions = np.array([
        -0.5, -0.5,
        0.5, -0.5,
        0.0,  0.5
    ], dtype=np.float32)

    colors = np.array([
        1, 0, 0,
        0, 1, 0,
        0, 0, 1
    ], dtype=np.float32)

    intensities = np.array([
        1, 0.5, 0
    ], dtype=np.float32)

    gpu_triangle = pipeline.vertex_list(3, GL.GL_TRIANGLES)
    gpu_triangle.position = positions
    gpu_triangle.color = colors
    gpu_triangle.intensity = intensities

    def update(dt):
        global TIME
        TIME += dt*5
        color_change = np.array([
            np.sin(TIME), 0, np.cos(TIME),
            0, np.sin(TIME), 0,
            np.cos(TIME), 0, np.sin(TIME)
        ], dtype=np.float32) + 0.5
        gpu_triangle.color = color_change

    @controller.event
    def on_draw():
        GL.glClearColor(0, 0, 0, 1.0)
        controller.clear()
        pipeline.use()
        gpu_triangle.draw(GL.GL_TRIANGLES)

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
