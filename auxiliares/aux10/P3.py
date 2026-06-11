from ctypes.wintypes import SIZE
from numpy._core.fromnumeric import sort
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock
import pyglet

import sys, os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
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

from utils import colliders


class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.zeros(3)
        self.velocity = np.zeros(3)
        self.speed = 5
        self.collider = colliders.AABB("player", [-0.4, -0.4, -0.4], [0.4, 0.4, 0.4])

    def physics_update(self, dt):
        self.update()
        dir = self.direction[2] * self.forward + self.direction[0] * self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.velocity += dir * self.speed
        self.position += self.velocity * dt
        self.collider.set_position(self.position)
        self.velocity = np.zeros(3)
        self.focus = self.position + self.forward

    # P3: Método para resolver colisiones de manera a posteriori
    def resolve_collision(self, colliders_list):
        for collider in colliders_list:
            # Si en el intertanto ya no colisionan, se ignora
            if not collider.detect_collision(self.collider):
                continue

            # Calculamos las distancias de penetración en los extremos de las cajas
            d1 = collider.min - self.collider.max
            d2 = collider.max - self.collider.min

            # Elegimos la distancia más corta por cada eje
            dist = d1 if np.linalg.norm(d1) < np.linalg.norm(d2) else d2

            # Buscamos cuál es el eje de mínima penetración para corregir solo esa componente
            min_dist = abs(dist[0])
            desplz = np.array([dist[0], 0.0, 0.0])

            for i in range(3):
                t = abs(dist[i])
                if t < min_dist:
                    min_dist = t
                    desplz = np.zeros(3)
                    desplz[i] = dist[i]

            # Corregimos la posición de la cámara de manera inmediata (a posteriori)
            self.position += desplz
            # Sincronizamos inmediatamente el collider para el siguiente bloque de la lista
            self.collider.set_position(self.position)

        # Recalculamos el foco de la cámara tras las modificaciones de posición
        self.focus = self.position + self.forward


# P1: Mapeo de texturas
BLOCKS_UV = [
    [], # ID 0: Aire / Vacío
    [(27, 20), (27, 20), (27, 20), (27, 20), (28, 18), (23, 23)],  # ID 1: Bloque Normal
    [(13, 11), (13, 11), (13, 11), (13, 11), (13, 11), (13, 11)],  # ID 2: Bloque de Hielo
    [(5, 28), (5, 28), (5, 28), (5, 28), (5, 28), (5, 28)],        # ID 3: Bloque de Lava / Púas
]


def get_atlas_uv(xoffset, yoffset, atlas):
    dx = 16 / atlas.width
    dy = 16 / atlas.height
    return [
        dx * xoffset,
        dy * yoffset,
        dx * (xoffset + 1),
        dy * yoffset,
        dx * (xoffset + 1),
        dy * (yoffset + 1),
        dx * xoffset,
        dy * (yoffset + 1),
    ]


class MyBlock:
    def __init__(self, id) -> None:
        self.id = id
        self.position = np.zeros(3)


class MyChunk(Model):
    SIZE = 16
    COUNT = 16

    def __init__(self, id, atlas):
        super().__init__([], [], [], [])
        self.index_data = []
        self.blocks = np.full((MyChunk.COUNT, MyChunk.COUNT, MyChunk.COUNT), None, dtype=object)
        for y in range(MyChunk.COUNT):
            for z in range(MyChunk.COUNT):
                for x in range(MyChunk.COUNT):
                    self.blocks[y][z][x] = MyBlock(0)
        self.atlas = atlas
        self.id = id

    def init_gpu_data(self, pipeline):
        delta = MyChunk.SIZE / MyChunk.COUNT
        cube_positions = [(coord + 0.5) * delta for coord in shapes.Cube["position"]]
        cube_positions = np.reshape(cube_positions, (len(cube_positions) // 3, 3))
        deltaV = cube_positions.shape[0]
        vcount = 0
        for y in range(MyChunk.COUNT):
            for z in range(MyChunk.COUNT):
                for x in range(MyChunk.COUNT):
                    block = self.blocks[y][z][x]
                    block.position = np.array([x * delta, y * delta, z * delta])
                    if block.id == 0:
                        continue

                    for p in cube_positions:
                        self.position_data.extend(p + block.position)

                    for u, v in BLOCKS_UV[block.id]:
                        self.uv_data.extend(get_atlas_uv(u, v, self.atlas))

                    self.normal_data.extend(shapes.Cube["normal"])
                    self.index_data.extend([vcount + i for i in shapes.Cube["indices"]])
                    vcount += deltaV

        super().init_gpu_data(pipeline)


# P3: Modificación de la función para procesar y resolver las colisiones
def check_collisions(player, manager):
    collisions = manager.check_collision("player")
    if not collisions:
        return

    # Obtenemos las referencias de los objetos collider involucrados y resolvemos
    player.resolve_collision([manager[b] for b in collisions])


if __name__ == "__main__":

    controller = Controller(800, 600, "Auxiliar Colisiones - P3")
    controller.set_exclusive_mouse(True)

    fps_label = pyglet.text.Label(
        text="FPS: 0.00",
        font_name="Arial",
        font_size=14,
        x=controller.width - 10,
        y=controller.height - 10,
        anchor_x="right",
        anchor_y="top",
        color=(255, 255, 255, 255)
    )

    shaders_folder = os.path.join(os.path.dirname(__file__), "shaders")
    pipeline = init_pipeline(
        shaders_folder + "/phong.vert", shaders_folder + "/phong.frag"
    )
    root = os.path.dirname(__file__)

    cam = MyCam([0.5, 4.0, 0.5])
    world = SceneGraph(cam)

    atlas = Texture(
        root + "/../../assets/atlas.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST
    )

    chunks = [MyChunk(i, atlas) for i in range(9)]

    manager = colliders.CollisionManager()
    manager.add_collider(cam.collider)

    for c in chunks:
        for z in range(MyChunk.COUNT):
            for x in range(MyChunk.COUNT):
                tipo_bloque = np.random.randint(0, 4) 
                c.blocks[0][z][x] = MyBlock(tipo_bloque)
                
                if tipo_bloque != 0:
                    manager.add_collider(colliders.AABB(f"{c.id}({x},0,{z})", [0, 0, 0], [1, 1, 1]))

    initial_positions = [
        [0, 0, 0],
        [MyChunk.SIZE, 0, 0],
        [-MyChunk.SIZE, 0, 0],
        [0, 0, MyChunk.SIZE],
        [MyChunk.SIZE, 0, MyChunk.SIZE],
        [-MyChunk.SIZE, 0, MyChunk.SIZE],
        [0, 0, -MyChunk.SIZE],
        [MyChunk.SIZE, 0, -MyChunk.SIZE],
        [-MyChunk.SIZE, 0, -MyChunk.SIZE],
    ]
    for c, pos in zip(chunks, initial_positions):
        world.add_node(
            f"chunk{c.id}",
            mesh=c,
            pipeline=pipeline,
            material=Material(),
            texture=atlas,
            position=pos,
        )

    world.add_node(
        "sun",
        light=DirectionalLight(ambient=[0.2, 0.2, 0.2]),
        pipeline=pipeline,
        rotation=[-np.pi / 4, -np.pi / 4, 0],
    )

    world.update()

    for c in chunks:
        c_pos = world.find_position(f"chunk{c.id}")
        for z in range(MyChunk.COUNT):
            for x in range(MyChunk.COUNT):
                if c.blocks[0][z][x].id == 0:
                    continue

                local_pos = c.blocks[0][z][x].position
                manager.set_position(f"{c.id}({x},0,{z})", local_pos + c_pos)

    @controller.event
    def on_draw():
        controller.clear()
        glEnable(GL_DEPTH_TEST)
        world.draw()
        
        glDisable(GL_DEPTH_TEST)
        fps_label.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[2] = 1
        if symbol == key.S:
            cam.direction[2] = -1
        if symbol == key.A:
            cam.direction[0] = 1
        if symbol == key.D:
            cam.direction[0] = -1

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[2] = 0
        if symbol == key.A or symbol == key.D:
            cam.direction[0] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * 0.001
        cam.pitch += dy * 0.001
        cam.pitch = math.clamp(cam.pitch, -(np.pi / 2 - 0.01), np.pi / 2 - 0.01)

    def update(dt):
        world.update()
        cam.physics_update(dt)
        check_collisions(cam, manager)
        
        fps = 1 / dt if dt > 0 else 0
        fps_label.text = f"FPS: {fps:.2f}"

    clock.schedule_interval(update, 1 / 1500)
    run()