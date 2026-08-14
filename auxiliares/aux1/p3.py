import pyglet
import numpy as np
from pyglet.gl import *


WIDTH = 600
HEIGHT = 600
DEFINITION = 36
TIME = 0

window = pyglet.window.Window(WIDTH, HEIGHT, "Auxiliar 2")

def create_portal(x, y, radius):
    # Discretizamos un circulo en DEFINITION pasos
    # Cada punto tiene 3 coordenadas y 3 componentes de color
    # Consideramos tambien el centro del circulo
    positions = np.zeros((DEFINITION + 1)*3, dtype=np.float32) 
    colors = np.zeros((DEFINITION + 1) * 3, dtype=np.float32)
    dtheta = 2*np.pi / DEFINITION

    for i in range(DEFINITION):
        theta = i*dtheta
        positions[i*3:(i+1)*3] = [x + np.cos(theta)*radius, y + np.sin(theta)*radius, 0.0]

    # Finalmente agregamos el centro
    positions[3*DEFINITION:] = [x, y, 0.0]

    return positions

def create_portal_indices():
    # Ahora calculamos los indices
    indices = np.zeros(3*( DEFINITION + 1 ), dtype=np.int32)
    for i in range(DEFINITION):
        # Cada triangulo se forma por el centro, el punto actual y el siguiente
        indices[3*i: 3*(i+1)] = [DEFINITION, i, i+1]
   
    # Completamos el circulo (pueden borrar esta linea y ver que pasa)
    indices[3*DEFINITION:] = [DEFINITION, DEFINITION - 1, 0]
    return indices


if __name__ == "__main__":
    # Creamos nuestros shaders
    vertex_source = """
#version 330

in vec3 position;
in vec3 color;

out vec3 fragColor;

void main() {
    fragColor = color;
    gl_Position = vec4(position, 1.0f);
}
    """

    fragment_source = """
#version 330

in vec3 fragColor;
out vec4 outColor;

void main()
{
    outColor = vec4(0.2, 0.6, 1.0, 1.0);
}
    """

    special_vertex_source = """
    #version 330 core
    in vec3 position;
    in vec3 color;

    uniform float time;
    uniform vec2 center; // Centro del círculo para escalar desde su propio eje

    out vec3 fragColor;

    void main() {
        fragColor = color;
        
        // Factor de escala oscilante entre 0.6 y 1.4
        float scale = 1.0 + 0.4 * sin(time * 4.0);

        // Escalamos la posición relativa al centro del círculo
        vec2 scaled_pos = center + (position.xy - center) * scale;

        gl_Position = vec4(scaled_pos, position.z, 1.0);
    }
    """

    special_fragment_source = """
    #version 330 core
    in vec3 fragColor;
    uniform float time;

    out vec4 outColor;

    void main() {
        // Modulación dinámica del color con funciones trigonométricas
        float r = 0.5 + 0.5 * sin(time * 3.0);
        float g = 0.5 + 0.5 * cos(time * 2.0);
        float b = 0.5 + 0.5 * sin(time * 5.0 + 1.5);

        outColor = vec4(r, g, b, 1.0);
    }
    """

    # Compilamos los shaders
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")

    vert_special_program = pyglet.graphics.shader.Shader(special_vertex_source, "vertex")
    frag_special_program = pyglet.graphics.shader.Shader(special_fragment_source, "fragment")

    # Creamos nuestro pipeline de rendering
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)
    pipeline_special = pyglet.graphics.shader.ShaderProgram(vert_special_program, frag_special_program)

    indices = create_portal_indices()

    # Portal 1 (Estable, Izquierda)
    circle_pos = create_portal(-0.4, 0.0, 0.35)
    circle_gpu = pipeline.vertex_list_indexed(DEFINITION + 1, GL_TRIANGLES, indices)
    circle_gpu.position[:] = circle_pos

    # Portal 2 (Inestable/Especial, Derecha)
    p2_x, p2_y = 0.4, 0.0
    special_pos = create_portal(p2_x, p2_y, 0.35)
    special_gpu = pipeline_special.vertex_list_indexed(DEFINITION + 1, GL_TRIANGLES, indices)
    special_gpu.position[:] = special_pos

    # Actualización del tiempo para la animación (60 FPS)
    def update(dt):
        global TIME
        TIME += dt

    pyglet.clock.schedule_interval(update, 1/60)

    @window.event
    def on_draw():

        # Esta linea limpia la pantalla entre frames
        window.clear()
        glClearColor(0.1, 0.1, 0.1, 0.0)

        pipeline.use()
        circle_gpu.draw(GL_TRIANGLES)

        pipeline_special.use()
        pipeline_special["time"] = TIME
        pipeline_special["center"] = (p2_x, p2_y)
        special_gpu.draw(GL_TRIANGLES)


    pyglet.app.run()


    
