import pyglet
from pyglet.gl import *
import numpy as np
import os
import sys

# Para facilitar el uso de módulos, obtenemos el camino a la raiz del repositorio (CC3501)
root = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))
# Y añadimos este camino a sys.path. De esta forma python sabe donde buscar
sys.path.append(root)

# Ahora importamos las librerias del curso sin problema
from utils.scene_graph import *
from utils.helpers import mesh_from_file


#Controller
class Controller(pyglet.window.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0.0

WIDTH = 1000
HEIGHT = 1000
window = Controller(WIDTH, HEIGHT, "Aux 5")


if __name__ == "__main__":
    #Corregir el shader para que funcione con los uniforms del grafo de escena
    #u_color y u_model
    vertex_source = """
#version 330

in vec3 position;
uniform vec3 u_color = vec3(1.0);


uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

out vec3 fragColor;

void main() {
    fragColor = u_color;
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
}
    """

    fragment_source = """
#version 330

in vec3 fragColor;
out vec4 outColor;

void main()
{
    outColor = vec4(fragColor, 1.0f);
}
    """

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)


    vaca_magica = mesh_from_file(root + "/assets/cow.obj")[0]['mesh']
    orb = mesh_from_file(root + "/assets/sphere.obj")[0]['mesh']

    vaca_magica.init_gpu_data(pipeline)
    orb.init_gpu_data(pipeline)

    vacaTransform = tr.translate(0, 2, 3)

    orbTransform = tr.translate(0, 0, 3)

    
    #Matriz perspectiva
    pipeline["projection"] = pyglet.math.Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90)
    #Camara estática en (0, 1, -0.5) que mira hacia el (0, 1, 1)
    pipeline["view"] = pyglet.math.Mat4.look_at(pyglet.math.Vec3(0, 1, -.5), pyglet.math.Vec3(0, 1, 1), pyglet.math.Vec3(0, 1, 0))


    def update(dt):
        #Pasa el tiempo
        window.time += dt


    @window.event
    def on_draw():
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.1, 0.1, 0.1, 0.0)
        
        window.clear()

        pipeline.use()

        pipeline["u_model"] = np.reshape(vacaTransform, (16,1), order="F")
        pipeline["u_color"] = np.array([1, 0, 1], dtype=np.float32)
        vaca_magica.draw()

        pipeline["u_model"] = np.reshape(orbTransform, (16,1), order="F")
        pipeline["u_color"] = np.array([0, 1, 0], dtype=np.float32)
        orb.draw()


    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
