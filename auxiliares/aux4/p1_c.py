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
window = Controller(WIDTH, HEIGHT, "Aux 4")


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


    vaca_magica = mesh_from_file(__file__ + "/../../../assets/cow.obj")[0]['mesh']
    orb = mesh_from_file(__file__ + "/../../../assets/sphere.obj")[0]['mesh']

    graph = SceneGraph()

    #Nodo que contiene al resto
    graph.add_node("vaca_orbs", rotation=[0, np.pi/4, 0])

    #Vaca
    graph.add_node("vaca",
                   attach_to="vaca_orbs",
                   mesh=vaca_magica,
                   pipeline=pipeline,
                   color = [1, 1, 1])
    
    #Orbs
    graph.add_node("orb1",
                   attach_to="vaca_orbs",
                   mesh=orb,
                   pipeline=pipeline,
                   color = [1, 1, 0],
                   scale=[0.2, 0.2, 0.2])
    graph.add_node("orb2",
                   attach_to="vaca_orbs",
                   mesh=orb,
                   pipeline=pipeline,
                   color = [1, 1, 0],
                   scale=[0.2, 0.2, 0.2])
    graph.add_node("orb3",
                   attach_to="vaca_orbs",
                   mesh=orb,
                   pipeline=pipeline,
                   color = [1, 1, 0],
                   scale=[0.2, 0.2, 0.2])
    
    #Matriz perspectiva
    pipeline["projection"] = pyglet.math.Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90)
    #Camara estática en (0, 1, -0.5) que mira hacia el (0, 1, 1)
    pipeline["view"] = pyglet.math.Mat4.look_at(pyglet.math.Vec3(0, 1, -.5), pyglet.math.Vec3(0, 1, 1), pyglet.math.Vec3(0, 1, 0))


    def update(dt):
        #Pasa el tiempo
        window.time += dt

        graph.update()

        #Oscilación de arriba a abajo
        graph["vaca_orbs"]["position"] = [0, np.cos(window.time), 3]

        #Rotación de los orbs al rededor de la vaca
        graph["orb1"]["position"] = [np.cos(2*window.time), 0.5, np.sin(2*window.time)]
        graph["orb2"]["position"] = [0, 0.5 + np.cos(2*window.time), np.sin(2*window.time)]
        graph["orb3"]["position"] = [-np.cos(2*window.time), 0.5, -np.sin(2*window.time)]


    @window.event
    def on_draw():
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.1, 0.1, 0.1, 0.0)
        
        window.clear()

        #Dibuje el grafo
        graph.draw()


    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
