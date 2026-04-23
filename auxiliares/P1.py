import pyglet
from pyglet.gl import *
from pyglet.math import Mat4, Vec3
from pyglet.window import Window
from pyglet.window import key
from pyglet.graphics.shader import Shader, ShaderProgram
import trimesh as tm
import numpy as np
import os
import sys

# Para facilitar el uso de módulos, obtenemos el camino a la raiz del repositorio (CC3501)
root = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))
# Y añadimos este camino a sys.path. De esta forma python sabe donde buscar
sys.path.append(root)

from utils.scene_graph import *
from utils.helpers import mesh_from_file
from utils.drawables import Model
from utils import shapes


#Controller
class Controller(pyglet.window.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0.0
        self.is_perspective = True
        self.camera_index = 0


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

    #Cargamos los distintos objetos
    vaca = mesh_from_file(__file__ + "/../../../assets/cow.obj")[0]['mesh']
    rata = mesh_from_file(__file__ + "/../../../assets/rat.obj")[0]['mesh']
    esfera = mesh_from_file(__file__ + "/../../../assets/sphere.obj")[0]['mesh']
    cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])    #Para el piso y la alfombra


    #Grafo de escena
    graph = SceneGraph()
    graph.add_node("scene")

    graph.add_node("floor", attach_to="scene")
    graph.add_node("grass", attach_to="floor",
                            mesh=cube, color=shapes.GREEN,
                            pipeline=pipeline,
                            scale=[5, 0.01, 5],
                            position=[0, 0, 0]
                        )
    graph.add_node("rug", attach_to="floor",
                            mesh=cube, color=shapes.RED,
                            pipeline=pipeline,
                            scale=[5, 0.011, 0.8],
                            position=[0, 0, 0]
                        )
    
    graph.add_node("rat_ball1", attach_to="scene",
                            position=[0.3, 0.06, -0.5],
                            scale=[0.1, 0.1, 0.1],
                            rotation=[0,-90,0]
                            )
    graph.add_node("ball1", attach_to="rat_ball1",
                            mesh=esfera, color=shapes.MAGENTA,
                            pipeline=pipeline,
                            position=[0, 0, 0]
                        )
    graph.add_node("rat1", attach_to="rat_ball1",
                            mesh=rata, color=shapes.GRAY,
                            pipeline=pipeline,
                            position=[0, 0.7, 0]
                        )
    
    graph.add_node("rat_ball2", attach_to="scene",
                            position=[-0.5, 0.06, 0.5],
                            scale=[0.1, 0.1, 0.1],
                            rotation=[0,-90,0]
                            )
    graph.add_node("ball2", attach_to="rat_ball2",
                            mesh=esfera, color=shapes.ORANGE,
                            pipeline=pipeline,
                            position=[0, 0, 0]
                        )
    graph.add_node("rat2", attach_to="rat_ball2",
                            mesh=rata, color=shapes.GRAY,
                            pipeline=pipeline,
                            position=[0, 0.7, 0]
                        )
    
    graph.add_node("rat_ball3", attach_to="scene",
                            position=[-0.5, 0.06, 2],
                            scale=[0.1, 0.1, 0.1],
                            rotation=[0,-90,0]
                            )
    graph.add_node("ball3", attach_to="rat_ball3",
                            mesh=esfera, color=shapes.ORANGE,
                            pipeline=pipeline,
                            position=[0, 0, 0]
                        )
    graph.add_node("rat3", attach_to="rat_ball3",
                            mesh=rata, color=shapes.GRAY,
                            pipeline=pipeline,
                            position=[0, 0.7, 0]
                        )
    
    graph.add_node("vaca", attach_to="scene",
                            mesh=vaca, color=shapes.BROWN,
                            pipeline=pipeline,
                            scale=[0.3, 0.3, 0.3],
                            position=[0, 0.2, 0]
                        )
    


    #Matriz perspectiva
    pipeline["projection"] = pyglet.math.Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90)

    #Camara
    pipeline["view"] = pyglet.math.Mat4.look_at(
        pyglet.math.Vec3(0.0, 0.2, -1),  # posición inicial de la cámara            
        pyglet.math.Vec3(0, 0, 0),       # punto al que mira la cámara
        pyglet.math.Vec3(0, 1, 0))       # vector "arriba"

    def update(dt):
        window.time += dt
        graph.update()


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