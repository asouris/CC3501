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
        # Inicializamos la cámara en la posición real de los ojos para evitar pantallas negras
        super().__init__(position + np.array([0.0, 1.7, 0.0]), camera_type)
        self.direction = np.zeros(3)
        self.velocity = np.zeros(3)
        self.speed = 5
        
        # Guardamos la posición física del "suelo/pies" del jugador
        self.player_pos = np.array(position, dtype=float)
        
        # P5: El AABB ahora está alineado perfectamente con los pies del jugador
        self.collider = colliders.AABB("player", [-0.4, 0.0, -0.4], [0.4, 1.8, 0.4])
        self.collider.set_position(self.player_pos)
        
        # Atributos físicos para el movimiento dinámico (Gravedad y Salto)
        self.gravity = -18.0
        self.vertical_velocity = 0.0
        self.jump_strength = 7.0
        self.is_on_ground = False
        self.on_ice = False  

        # Altura de los ojos sobre el suelo
        self.eye_height = 1.7

    def physics_update(self, dt):
        self.update()
        
        # 1. Calculamos dirección horizontal deseada por teclado
        dir_h = self.direction[2] * self.forward + self.direction[0] * self.right
        dir_h[1] = 0.0  # Aislar movimiento estrictamente al plano horizontal
        dir_norm = np.linalg.norm(dir_h)
        if dir_norm:
            dir_h /= dir_norm
            
        # P5: Lógica de movimiento en el hielo o normal
        if self.on_ice:
            self.velocity[0] = self.velocity[0] * 0.95 + dir_h[0] * self.speed * 0.05
            self.velocity[2] = self.velocity[2] * 0.95 + dir_h[2] * self.speed * 0.05
        else:
            self.velocity[0] = dir_h[0] * self.speed
            self.velocity[2] = dir_h[2] * self.speed

        # 2. Aplicamos la gravedad acumulativa sobre el eje Y
        self.vertical_velocity += self.gravity * dt
        self.velocity[1] = self.vertical_velocity

        # 3. Aplicamos el desplazamiento físico a los pies del jugador
        self.player_pos += self.velocity * dt
        self.collider.set_position(self.player_pos)
        
        # Sincronizamos la posición de renderizado de la cámara (Ojos = Pies + Altura de ojos)
        self.position = self.player_pos + np.array([0.0, self.eye_height, 0.0])
        
        # Reseteamos flags de suelo antes del check de colisiones
        self.is_on_ground = False
        self.on_ice = False
        self.focus = self.position + self.forward

    # P5: Resolución de colisiones con lógica adaptada al material del bloque impactado
    def resolve_collision(self, colliders_list, chunks):
        for collider in colliders_list:
            if not collider.detect_collision(self.collider):
                continue

            d1 = collider.min - self.collider.max
            d2 = collider.max - self.collider.min
            dist = d1 if np.linalg.norm(d1) < np.linalg.norm(d2) else d2

            # Determinamos cuál es el eje de mínima penetración
            min_dist = abs(dist[0])
            axis = 0
            for i in range(3):
                if abs(dist[i]) < min_dist:
                    min_dist = abs(dist[i])
                    axis = i

            # Construimos el vector de corrección posicional
            desplz = np.zeros(3)
            desplz[axis] = dist[axis]

            # Corregimos posición de los pies del jugador de manera a posteriori
            self.player_pos += desplz
            self.collider.set_position(self.player_pos)

            # Re-calculamos la posición de la cámara tras la corrección
            self.position = self.player_pos + np.array([0.0, self.eye_height, 0.0])

            # --- LÓGICA DE EVENTOS DE BLOQUE (P5) ---
            if axis == 1 and dist[1] > 0:
                self.vertical_velocity = 0.0
                self.is_on_ground = True
                
                try:
                    name = collider.name
                    parts = name.split("(")
                    c_id = int(parts[0])
                    coords = parts[1].replace(")", "").split(",")
                    bx = int(coords[0])
                    bz = int(coords[2])
                    
                    block_id = chunks[c_id].blocks[0][bz][bx].id
                    
                    if block_id == 2:    # Bloque de Hielo
                        self.on_ice = True
                    elif block_id == 3:  # Bloque de Lava / Púas (Muerte)
                        # Teletransportamos al origen de coordenadas (Reset de nivel)
                        self.player_pos = np.array([0.5, 4.0, 0.5])
                        self.vertical_velocity = 0.0
                        self.velocity = np.zeros(3)
                        self.collider.set_position(self.player_pos)
                        self.position = self.player_pos + np.array([0.0, self.eye_height, 0.0])
                        break
                except:
                    pass

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


# P5: Verificación de colisiones estrecha (Narrow Phase directa e interactiva)
def check_collisions(player, manager, chunks):
    collisions = manager.check_collision("player")
    if not collisions:
        return

    player.resolve_collision([manager[b] for b in collisions], chunks)


if __name__ == "__main__":

    controller = Controller(800, 600, "Auxiliar Colisiones - P5 (Gravedad y Estados)")
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

    # Posicionamos al jugador basándonos en sus PIES. La clase se encarga de subir los ojos internamente.
    cam = MyCam([0.5, 4.0, 0.5])
    world = SceneGraph(cam)

    atlas = Texture(
        root + "/../../assets/atlas.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST
    )

    chunks = [MyChunk(i, atlas) for i in range(9)]

    manager = colliders.CollisionManager()
    manager.add_collider(cam.collider)

    # Generación de la grilla plana original
    for c in chunks:
        for z in range(MyChunk.COUNT):
            for x in range(MyChunk.COUNT):
                tipo_bloque = np.random.randint(1, 4) 
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

    # Sincronización exacta de posiciones globales en el manager
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
            
        if symbol == key.SPACE and cam.is_on_ground:
            cam.vertical_velocity = cam.jump_strength

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
        check_collisions(cam, manager, chunks)
        
        fps = 1 / dt if dt > 0 else 0
        fps_label.text = f"FPS: {fps:.2f}"

    clock.schedule_interval(update, 1 / 60)
    run()