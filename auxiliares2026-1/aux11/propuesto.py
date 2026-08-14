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
        
        # Variables de la cámara y luz
        self.light_mode = False
        self.light_distance = 1
        
        # Animación del Tiro
        self.tipo_tiro = 1
        self.t_tiro = 0.0
        
        # Animación del Arquero (Catmull-Rom)
        self.t_arquero = 0.0

class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0,0,0])
        self.speed = 4

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward

# --- FUNCIONES MATEMÁTICAS ---

def bezierCurve(t, P0, P1, P2, P3):
    return P0 * pow(1-t, 3) + P1 * 3 * t * pow(1-t, 2) + P2 * 3 * pow(t, 2) * (1-t) + P3 * pow(t, 3)

def catmull_rom(t, P0, P1, P2, P3):
    """
    Interpola suavemente entre P1 y P2. 
    P0 y P3 se usan para calcular las tangentes de entrada y salida.
    """
    t2 = t * t
    t3 = t2 * t
    
    # Ecuación polinómica de Catmull-Rom extraída de la matriz
    f0 = -0.5*t3 + t2 - 0.5*t
    f1 =  1.5*t3 - 2.5*t2 + 1.0
    f2 = -1.5*t3 + 2.0*t2 + 0.5*t
    f3 =  0.5*t3 - 0.5*t2
    
    return P0*f0 + P1*f1 + P2*f2 + P3*f3

# --- PUNTOS DE CONTROL ---

P_inicio = np.array([-8.0, 0.0, 0.0]) # Posición del delantero
P_arco   = np.array([ 8.0, 0.0, 0.0]) # Centro del arco

# Puntos de patrullaje del arquero en la línea del arco (Eje Z es lo ancho del arco)
# DUPLICAMOS el primero y el último para que Catmull-Rom pueda calcular las tangentes de los bordes.
puntos_arquero = [
    np.array([8.0, 0.0, -4.0]), # Duplicado inicial
    np.array([8.0, 0.0, -4.0]), # Poste izquierdo
    np.array([8.0, 1.5, -2.5]), # Salto al palo izquierdo
    np.array([8.0, 0.0,  0.0]), # Centro del arco
    np.array([8.0, 1.5,  2.5]), # Salto al palo derecho
    np.array([8.0, 0.0,  4.0]), # Poste derecho
    np.array([8.0, 0.0,  4.0])  # Duplicado final
]

# --- HELPER PARA CREAR MALLAS PROCEDURALES ---
def crear_modelo_trimesh(trimesh_obj):
    pos_data = trimesh_obj.vertices.flatten().tolist()
    idx_data = trimesh_obj.faces.flatten().tolist()
    norm_data = trimesh_obj.vertex_normals.flatten().tolist()
    # Inyectamos las UVs en cero para evitar el error de NoneType
    uv_data = [0.0] * (len(trimesh_obj.vertices) * 2)
    return Model(position_data=pos_data, uv_data=uv_data, normal_data=norm_data, index_data=idx_data)


if __name__ == "__main__":

    controller = Controller(1200, 1000, "Auxiliar: Catmull-Rom Arquero")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)
    flat_pipeline = init_pipeline(root + "/flat.vert", root + "/flat.frag") 
    cam = MyCam([0, 6, 15]) 

    # --- CREACIÓN DE GEOMETRÍA PROCEDURAL ---
    # 1. Pelota (Esfera)
    malla_pelota = crear_modelo_trimesh(tm.creation.icosphere(subdivisions=3, radius=0.4))
    
    # 2. Arquero (Cubo)
    malla_arquero = crear_modelo_trimesh(tm.creation.box(extents=[1.0, 1.0, 1.0]))
    
    # 3. Componentes del Arco (Cilindro)
    malla_poste = crear_modelo_trimesh(tm.creation.cylinder(radius=0.15, height=1.0, sections=16))
    # ----------------------------------------

    world = SceneGraph(cam)

    # Añadir Pelota (Blanca)
    world.add_node("pelota",
                   mesh=malla_pelota,
                   pipeline=flat_pipeline,
                   material=Material([1.0, 1.0, 1.0]), 
                   scale=[1.0, 1.0, 1.0],
                   position=P_inicio.tolist()
                   )
                   
    # Añadir Arquero (Morado y más alto que ancho)
    world.add_node("arquero",
                   mesh=malla_arquero,
                   pipeline=flat_pipeline,
                   material=Material([0.6, 0.2, 0.8]), # Color Morado
                   scale=[0.3, 1.5, 0.7], # Lo hacemos rectangular para que parezca personaje
                   position=[0, 0, 0]
                   )

    # --- Construcción del Arco ---
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
                   scale=[0.2, ancho_arco*4, 0.2],
                   # Lo posicionamos arriba, uniendo los dos postes
                   position=[P_arco[0], alto_arco, P_arco[2]]
                   )

    world.add_node("sun",
                   pipeline=flat_pipeline,
                   light=DirectionalLight(ambient=[.6, .6, .6], diffuse=[.6, .6, .6]),
                   rotation=[-np.pi/2, 0, 0]
                   )

    def update(dt):
        # 1. ACTUALIZAR TIRO DE LA PELOTA
        controller.t_tiro += dt * 0.5
        if controller.t_tiro > 1.0:
            controller.t_tiro = 0.0
            
        t_pelota = controller.t_tiro
        if controller.tipo_tiro == 1:
            pos_pelota = P_inicio * (1 - t_pelota) + P_arco * t_pelota # Lerp
        elif controller.tipo_tiro == 2:
            pos_pelota = bezierCurve(t_pelota, P_inicio, P_inicio + np.array([4,8,0]), P_arco + np.array([-4,8,0]), P_arco)
        elif controller.tipo_tiro == 3:
            pos_pelota = bezierCurve(t_pelota, P_inicio, P_inicio + np.array([4,0,10]), P_arco + np.array([-4,0,-10]), P_arco)

        world["pelota"]["position"] = pos_pelota.tolist()

        # 2. ACTUALIZAR PATRULLAJE DEL ARQUERO (CATMULL-ROM)
        controller.t_arquero += dt * 0.8
        
        # Cantidad de segmentos válidos (N puntos - 3)
        num_segmentos = len(puntos_arquero) - 3
        
        # Hacemos que el tiempo global rebote de ida y vuelta (Ping-Pong) para que no se teletransporte
        t_rebote = np.abs((controller.t_arquero % (num_segmentos * 2)) - num_segmentos)
        
        # Separar el tramo actual (parte entera) del t local del segmento (parte decimal)
        segmento_actual = int(t_rebote)
        t_local = t_rebote - segmento_actual
        
        # Evitamos desbordamiento en el índice máximo
        if segmento_actual >= num_segmentos:
            segmento_actual = num_segmentos - 1
            t_local = 1.0

        # Obtener los 4 puntos necesarios para interpolar el segmento actual
        P0 = puntos_arquero[segmento_actual]
        P1 = puntos_arquero[segmento_actual + 1]
        P2 = puntos_arquero[segmento_actual + 2]
        P3 = puntos_arquero[segmento_actual + 3]
        
        # Interpolar la posición
        pos_arquero = catmull_rom(t_local, P0, P1, P2, P3)
        
        # Para que el arquero no se entierre en el suelo, levantamos su posición base sumando la mitad de su escala Y
        pos_arquero[1] += 1.0 
        
        world["arquero"]["position"] = pos_arquero.tolist()

        world.update()
        cam.time_update(dt)

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.2, 0.7, 0.3, 1) # Cancha verde
        glEnable(GL_DEPTH_TEST)
        world.draw()

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.SPACE: controller.light_mode = not controller.light_mode
        if symbol == key.W: cam.direction[0] = 1
        if symbol == key.S: cam.direction[0] = -1
        if symbol == key.A: cam.direction[1] = 1
        if symbol == key.D: cam.direction[1] = -1
        
        # Cambiar el tipo de tiro para probar al arquero
        if symbol == key._1: controller.tipo_tiro = 1; controller.t_tiro = 0.0
        if symbol == key._2: controller.tipo_tiro = 2; controller.t_tiro = 0.0
        if symbol == key._3: controller.tipo_tiro = 3; controller.t_tiro = 0.0

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S: cam.direction[0] = 0
        if symbol == key.A or symbol == key.D: cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * .001
        cam.pitch += dy * .001
        cam.pitch = math.clamp(cam.pitch, -(np.pi/2 - 0.01), np.pi/2 - 0.01)

    clock.schedule_interval(update, 1/60)
    run()