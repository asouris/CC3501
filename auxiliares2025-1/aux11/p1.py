from time import sleep
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

import sys, os
import numpy as np
from random import *

import pymunk

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.helpers import init_axis, mesh_from_file, init_pipeline
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import (
    Texture,
    Model,
    SpotLight,
    PointLight,
    DirectionalLight,
    Material,
)

# Controller de siempre, lo usamos para guardar el tiempo transcurrido
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.bodies = []

# Camara que se mueve libremente usando las teclas
# El control con las teclas está en el update y en el evento 
# Esta camara se le debe pasar al grafo de escena
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 2

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward



if __name__ == "__main__":

    controller = Controller(1000, 1000, "Tarea 4")
    controller.set_exclusive_mouse(True)

    # Shaders de color
    # Si quiere utilizar texturas debe cambiar este shader
    # Ojo que el modelo de la esfera no trae coordenadas UV pq lo que no lo puede meter a un shader con texturas
    # Puede usar otro modelo si lo encuentra en internet
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    print(root)

    with open(root +  "/shaders/color_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(root +  "/shaders/color_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = Shader(color_vertex_source_code, "vertex")
    frag_program = Shader(color_fragment_source_code, "fragment")
    pipeline = ShaderProgram(vert_program, frag_program)

    #pipeline con texturas
    with open(root +  "/shaders/textured_mesh_lit.vert") as f:
        texture_vertex_source_code = f.read()

    with open(root +  "/shaders/textured_mesh_lit.frag") as f:
        texture_fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = Shader(texture_vertex_source_code, "vertex")
    frag_program = Shader(texture_fragment_source_code, "fragment")
    texturePipeline = ShaderProgram(vert_program, frag_program)

    cam = MyCam([0, 3, 10])

    # Axis para debuguear desactivelo antes de entregar, se ve feo
    axis = init_axis(cam)

    # Grafo inicial
    world = SceneGraph(cam)

    # Meshes
    #sphere = mesh_from_file(root + "/assets/sphere.obj")[0]['mesh']
    cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"], normal_data=shapes.Cube["normal"])

    world.add_node(
        "sun",
        light=DirectionalLight(ambient=[0.2, 0.2, 0.2]),
        pipeline=[pipeline, texturePipeline],
        rotation=[-np.pi / 4, -np.pi / 4, 0],
    )

    space = pymunk.Space()
    space.gravity = (0, -9.81)

    groundBody = pymunk.Segment(space.static_body, (-50, 0), (50, 0), 0)
    groundBody.friction = 1.0

    space.add(groundBody)

    quadUV = [
        0, 0,
        10, 0,
        10, 10,
        0, 10
    ]
    quad = Model(shapes.Square["position"], index_data=shapes.Square["indices"], normal_data=shapes.Square["normal"], uv_data=quadUV)

    world.add_node("floor",
              pipeline=texturePipeline,
              mesh = quad,
              rotation = [-np.pi/2, 0, 0],
              scale = [50, 50, 1],
              material=Material(),
              texture=Texture(root + "/assets/grass.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST, sWrapMode=GL_REPEAT, tWrapMode=GL_REPEAT))
    
    # def randomCube():
    #     mass = 1.0
    #     size = 0.5
    #     points = [(-size, -size), (-size, size), (size, size), (size, -size)]

    #     body = pymunk.Body(mass, pymunk.moment_for_poly(mass, points, (0, 0)))
    #     rx = randint(3, 7)
    #     ry = randint(4, 12)
    #     body.position = (rx, ry)

    #     shape = pymunk.Poly(body, points)

    #     shape.friction = 1.5
    #     space.add(body, shape)
    #     index = str(len(controller.bodies))
    #     controller.bodies.append(("body_" + index, body))

    #     world.add_node("body_" + index,
    #                     mesh=cube, 
    #                     pipeline=pipeline, 
    #                     material=Material(),
    #                     position = [body.position[0], body.position[1], -5]
    #                     )

    mass = 1.0
    size = 0.5
    points = [(-size, -size), (-size, size), (size, size), (size, -size)]

    body = pymunk.Body(mass, pymunk.moment_for_poly(mass, points, (0, 0)))
    # rx = randint(3, 7)
    # ry = randint(4, 12)
    body.position = (0, 10)

    shape = pymunk.Poly(body, points)

    shape.friction = 1.5
    space.add(body, shape)
    index = str(len(controller.bodies))
    controller.bodies.append(("body_" + index, body))

    world.add_node("body_" + index,
                    mesh=cube, 
                    pipeline=pipeline, 
                    material=Material(),
                    position = [body.position[0], body.position[1], -5]
                    )

    # Creamos los 
    # obstáculos

    # numOfCubes = 10
    # while numOfCubes > 0:
    #     randomCube()
    #     numOfCubes-=1


    # mass = 1
    # circleBody = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, 0.5))
    # circleBody.position = (-8, 0)
    # circle = pymunk.Circle(circleBody, 0.5)  
    # space.add(circleBody, circle)

    # world.add_node("bomba",
    #                pipeline=pipeline,
    #                mesh = sphere,
    #                material=Material(ambient=[1, 0, 0.5]),
    #                position=[-8, 0, -5],
    #                scale=[0.5, 0.5, 0.5])



    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1

        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1

        # if symbol == key.SPACE:
        #     randomCube()

        # if symbol == key.I:
        #     circleBody.apply_impulse_at_local_point((15, 8))


    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = math.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)


    # UPDATE
    def update(dt):
        controller.time += dt

        world.update()
        axis.update()
        cam.time_update(dt)

        space.step(dt)

        for b in controller.bodies:
            name = b[0]
            body = b[1]

            world[name]["position"] = [body.position[0], body.position[1], -5]

        # world["bomba"]["position"] = [circleBody.position[0], circleBody.position[1], -5]


    # DRAW
    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.8, 0.8, 0.8, 1.0)
        glEnable(GL_DEPTH_TEST)
        world.draw()
        axis.draw()


    clock.schedule_interval(update, 1 / 60)
    run()
