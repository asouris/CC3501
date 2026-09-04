import os
import sys

import numpy as np
import pyglet
from pyglet.gl import *

# Para facilitar el uso de módulos, obtenemos el camino a la raiz del repositorio (CC3501)
root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# Y añadimos este camino a sys.path. De esta forma python sabe donde buscar
sys.path.append(root)

import grafica.transformations as tr
from utils import shapes
from utils.drawables import Model

# Ahora importamos las librerias del curso sin problema
from utils.scene_graph import *

WIDTH = 1000
HEIGHT = 1000

#Controller
class Controller(pyglet.window.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0.0

WIDTH = 1000
HEIGHT = 1000
window = Controller(WIDTH, HEIGHT, "Aux 4")

if __name__ == "__main__":

    vertex_source = """
#version 330

in vec3 position;
uniform vec3 u_color = vec3(1.0);


uniform mat4 u_model;
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec3 fragColor;

void main() {
    fragColor = u_color;
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
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

    # Programa con shader básicos
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # A continuación se declaran los objetos que hay que ubicar en su lugar (debe conservar el scale)
    # Actualmente estan uno al lado del otro y a cada uno se le pasa su transformación
    head = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])
    head.init_gpu_data(pipeline)
    head_model = pyglet.math.Mat4.from_translation(pyglet.math.Vec3(-0.2, 0.2, 0)) @ pyglet.math.Mat4.from_scale(pyglet.math.Vec3(0.35*0.2, 0.35*0.2, 0.35*0.2))

    chest = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])
    chest.init_gpu_data(pipeline)
    chest_model = pyglet.math.Mat4.from_translation(pyglet.math.Vec3(0, 0.2, 0)) @ pyglet.math.Mat4.from_scale(pyglet.math.Vec3(0.5*0.2, 1*0.2, 0.35*0.2))

    arm = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])
    arm.init_gpu_data(pipeline)
    arm_model = pyglet.math.Mat4.from_translation(pyglet.math.Vec3(0.2, 0.2, 0)) @ pyglet.math.Mat4.from_scale(pyglet.math.Vec3(0.2*0.2, 1*0.2, 0.2*0.2))


    # A continuacion estan los objetos que SI están bien puestos y se encuentran en el grafo de escena
    # Todos usan el cubo como geometría base y usan las transformaciones para modificarlo

    #Objeto base
    cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"])

    #Grafo de escena incompleto
    graph = SceneGraph()
    graph.add_node("body", rotation=[0, np.pi + np.pi/4, 0], scale=[0.2, 0.2, 0.2], position=[0, 0, 0]) # nodo sin geometría pero con transformaciones
    graph.add_node("left_leg", attach_to="body")    # nodo sin geometría
    graph.add_node("right_leg", attach_to="body")   # nodo sin geometría
    graph.add_node("left_upper_leg",
                            attach_to="left_leg",
                            mesh=cube, color=shapes.BLUE,
                            pipeline=pipeline,
                            position=[-0.2, -0.85, 0],
                            rotation=[0, 0, -0.15],
                            scale=[0.25, 0.75, 0.25],
                        )
    graph.add_node("right_upper_leg",
                            attach_to="right_leg",
                            mesh=cube, color=shapes.BLUE,
                            pipeline=pipeline,
                            position=[0.2, -0.85, 0],
                            rotation=[0, 0, 0.15],
                            scale=[0.25, 0.75, 0.25],
                        )
    graph.add_node("left_lower_leg",
                            attach_to="left_leg",
                            mesh=cube, color=shapes.DARK_BLUE,
                            pipeline=pipeline,
                            position=[-0.25, -1.5, 0],
                            scale=[0.2, 0.75, 0.2],
                        )
    graph.add_node("right_lower_leg",
                            attach_to="right_leg",
                            mesh=cube, color=shapes.DARK_BLUE,
                            pipeline=pipeline,
                            position=[0.25, -1.5, 0],
                            scale=[0.2, 0.75, 0.2],
                        )



    # Uniforms que simulan una cámara obtenidos a mano (sin clase cámara)
    pipeline["u_projection"] = pyglet.math.Mat4.perspective_projection(WIDTH/HEIGHT, 0.01, 100, 90)
    pipeline["u_view"] = pyglet.math.Mat4.look_at(pyglet.math.Vec3(0, 0, -.5), pyglet.math.Vec3(0, 0, 0), pyglet.math.Vec3(0, 1, 0))



    @window.event
    def on_draw():
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(1, 1, 1, 0.0)

        window.clear()

        pipeline.use()

        # Esto dibuja todos los objetos del grafo
        # En particular se encarga de pasar los uniforms correspondientes
        graph.draw()

        # Los siguientes objetos no estan en el grafo, por lo que hay que pasar sus uniforms manualmente e invocar draw()
        pipeline["u_model"] = head_model
        pipeline["u_color"] = shapes.CYAN
        head.draw(GL_TRIANGLES)

        pipeline["u_model"] = chest_model
        pipeline["u_color"] = shapes.RED
        chest.draw(GL_TRIANGLES)

        pipeline["u_model"] = arm_model
        pipeline["u_color"] = shapes.GREEN
        arm.draw(GL_TRIANGLES)




    def update(dt):
        #Pasa el tiempo
        window.time += dt
        graph.update()

        limb_rotation = np.sin(window.time * 5) / 2

        graph["left_leg"]["transform"] = tr.translate(0, -0.5, 0) @ tr.rotationX(-limb_rotation) @ tr.translate(0, 0.5, 0)
        graph["right_leg"]["transform"] = tr.translate(0, -0.5, 0) @ tr.rotationX(limb_rotation) @ tr.translate(0, 0.5, 0)

        lower_limb_rotation = np.cos(window.time * 5) / 3
        graph["left_lower_leg"]["transform"] = tr.translate(0, -1.125, 0) @ tr.rotationX(lower_limb_rotation + 0.25) @ tr.translate(0, 1.125, 0)
        graph["right_lower_leg"]["transform"] = tr.translate(0, -1.125, 0) @ tr.rotationX(lower_limb_rotation + 0.25) @ tr.translate(0, 1.125, 0)


    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
