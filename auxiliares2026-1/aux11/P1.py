from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock
import sys, os
import numpy as np
import trimesh as tm

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from utils.helpers import init_axis, init_pipeline, mesh_from_file
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils.drawables import Model, DirectionalLight, Material

class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.sky_color = np.array([0.2, 0.3, 0.5])
        self.intensity = 0.1
        self.light_mode = False
        self.light_dir = np.zeros(2)
        self.light_color = np.ones(3)
        self.light_distance = 1
        
        # --- VARIABLES PARA EL SUPER TIRO ---
        self.tipo_tiro = 1      # 1: Recto, 2: Bombeado, 3: Serpiente
        self.t_anim = 0.0       # Tiempo de la animación de 0 a 1
        self.velocidad = 0.5    # Qué tan rápido avanza t

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

# --- FUNCIONES MATEMÁTICAS 3D ---
# Interpolación Lineal para el tiro recto
def lerp(t, P0, P1):
    return P0 * (1 - t) + P1 * t

# Curva de Bezier para los tiros con efectos (Soporta vectores Numpy directos)
def bezierCurve(t, P0, P1, P2, P3):
    return P0 * pow(1-t, 3) + P1 * 3 * t * pow(1-t, 2) + P2 * 3 * pow(t, 2) * (1-t) + P3 * pow(t, 3)

# Puntos Base (3D) para el inicio y el arco
P_inicio = np.array([-8.0, 0.0, 0.0]) # Posición del delantero
P_arco   = np.array([ 8.0, 0.0, 0.0]) # Posición del arco

if __name__ == "__main__":

    controller = Controller(1200, 1000, "Auxiliar: Súper Tiros Dinámicos")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)
    flat_pipeline = init_pipeline(root + "/flat.vert", root + "/flat.frag") 
    cam = MyCam([0, 5, 15]) # Cámara un poco más arriba y atrás para ver el campo

    # Puedes cambiar "shark.obj" por una esfera (ej: "sphere.obj") si la tienes
    malla_pelota = mesh_from_file(root + "/sphere.obj")[0]['mesh']

    # --- PARCHE CORREGIDO PARA MODELOS SIN UV ---
    if malla_pelota.uv_data is None:
        # Usamos 'position_data' en lugar de 'vertices'
        num_vertices = len(malla_pelota.position_data) // 3
        malla_pelota.uv_data = [0.0] * (num_vertices * 2)
    # --------------------------------------------

    # --- CREACIÓN DE CILINDRO PROCEDURAL (Para el arco) ---
    # Generamos un cilindro matemático usando trimesh
    # Radio delgado (0.2) y altura (1.0). El centro estará en el origen.
    cilindro_tm = tm.creation.cylinder(radius=0.2, height=1.0, sections=16)
    
    pos_data_cil = cilindro_tm.vertices.flatten().tolist()
    idx_data_cil = cilindro_tm.faces.flatten().tolist()
    norm_data_cil = cilindro_tm.vertex_normals.flatten().tolist()
    
    num_vertices_cil = len(cilindro_tm.vertices)
    uv_data_cil = [0.0] * (num_vertices_cil * 2)

    malla_poste = Model(
        position_data=pos_data_cil,
        uv_data=uv_data_cil,
        normal_data=norm_data_cil,
        index_data=idx_data_cil
    )
    # -------------------------------------------

    world = SceneGraph(cam)

    world.add_node("pelota",
                   mesh=malla_pelota,
                   pipeline=flat_pipeline,
                   material=Material([1, 1, 1]), # Pelota blanca
                   rotation=[-np.pi/2, np.pi/2, np.pi],
                   scale=[1.0, 1.0, 1.0],
                   position=[P_inicio[0], P_inicio[1], P_inicio[2]]
                   )

    world.add_node("sun",
                   pipeline=flat_pipeline,
                   light=DirectionalLight(ambient=[.6, .6, .6], diffuse=[.6, .6, .6]),
                   rotation=[-np.pi/2, 0, 0]
                   )

    # Ancho y alto deseado del arco
    ancho_arco = 6.0
    alto_arco = 3.0

    # 1. Poste Izquierdo
    world.add_node("poste_izq",
                   mesh=malla_poste,
                   pipeline=flat_pipeline,
                   material=Material([0.9, 0.9, 0.9]), # Color gris claro/blanco
                   # Lo escalamos solo en el eje Y (altura)
                   scale=[0.2, alto_arco*2.5, 0.2], 
                   # Lo desplazamos en Z (ancho) y subimos la mitad de su altura en Y
                   position=[P_arco[0], alto_arco / 2.0, P_arco[2] - ancho_arco/2.0]
                   )

    # 2. Poste Derecho
    world.add_node("poste_der",
                   mesh=malla_poste,
                   pipeline=flat_pipeline,
                   material=Material([0.9, 0.9, 0.9]),
                   scale=[0.2, alto_arco*2.5, 0.2],
                   position=[P_arco[0], alto_arco / 2.0, P_arco[2] + ancho_arco/2.0]
                   )

    # 3. Travesaño Superior
    world.add_node("travesano",
                   mesh=malla_poste,
                   pipeline=flat_pipeline,
                   material=Material([0.9, 0.9, 0.9]),
                   # Lo acostamos: rotamos 90 grados en el eje X
                   rotation=[np.pi/2, 0, 0],
                   # Su largo (escala Y original del cilindro) será el ancho del arco
                   scale=[0.2, ancho_arco*2.5, 0.2],
                   # Lo posicionamos arriba, uniendo los dos postes
                   position=[P_arco[0], alto_arco, P_arco[2]]
                   )
    
    def update(dt):
        # 1. Avanzamos el parámetro t de 0.0 a 1.0
        controller.t_anim += dt * controller.velocidad
        if controller.t_anim > 1.0:
            controller.t_anim = 0.0 # Reiniciamos el tiro al llegar al arco

        t = controller.t_anim
        pos_actual = P_inicio

        # 2. Elegimos la trayectoria según el tipo de tiro seleccionado
        if controller.tipo_tiro == 1:
            # TIRO RECTO (Lerp)
            pos_actual = lerp(t, P_inicio, P_arco)

        elif controller.tipo_tiro == 2:
            # TIRO BOMBEADO / PARÁBOLA
            # Levantamos los puntos de control intermedios en el eje Y (Altura)
            P1 = P_inicio + np.array([ 4.0, 8.0, 0.0])
            P2 = P_arco   + np.array([-4.0, 8.0, 0.0])
            pos_actual = bezierCurve(t, P_inicio, P1, P2, P_arco)

        elif controller.tipo_tiro == 3:
            # TIRO DE LA SERPIENTE
            # Desviamos los puntos de control en el eje Z (Profundidad) para el zig-zag
            P1 = P_inicio + np.array([ 4.0, 0.0,  10.0]) # Va hacia la derecha (Z positivo)
            P2 = P_arco   + np.array([-4.0, 0.0, -10.0]) # Va hacia la izquierda (Z negativo)
            pos_actual = bezierCurve(t, P_inicio, P1, P2, P_arco)

        # 3. Aplicamos la posición en 3D al nodo de la escena
        world["pelota"]["position"] = [pos_actual[0], pos_actual[1], pos_actual[2]]

        world.update()
        cam.time_update(dt)
        controller.time += dt

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.2, 0.8, 0.2, 1) # Fondo verde estilo pasto de fútbol
        glEnable(GL_DEPTH_TEST)
        world.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        # Controles de cámara originales
        if symbol == key.SPACE: controller.light_mode = not controller.light_mode
        if symbol == key.W: cam.direction[0] = 1
        if symbol == key.S: cam.direction[0] = -1
        if symbol == key.A: cam.direction[1] = 1
        if symbol == key.D: cam.direction[1] = -1

        # Controles nuevos para el SUPER TIRO
        if symbol == key._1:
            controller.tipo_tiro = 1
            controller.t_anim = 0.0
            print("Activado: Tiro Recto")
        if symbol == key._2:
            controller.tipo_tiro = 2
            controller.t_anim = 0.0
            print("Activado: Tiro Bombeado")
        if symbol == key._3:
            controller.tipo_tiro = 3
            controller.t_anim = 0.0
            print("Activado: Tiro Serpiente")

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

    @controller.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        controller.light_distance += scroll_y*.01

    clock.schedule_interval(update, 1/60)
    run()