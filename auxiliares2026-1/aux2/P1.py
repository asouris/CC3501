# LIBRERIAS externas
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import clock

import sys, os
import numpy as np
# la siguiente linea le dice a python que cuando busque librerías, busque en la carpeta actual
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))

# MÓDULOS HECHOS POR EQUIPO DOCENTE (cuidado con las rutas)
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model

# Controla la ventana y el paso del tiempo
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0

# Esta clase nos ayuda a simular el comportamiento de una cámara
# Estan invitados a estudiar este código, pero lo veremos con más detención en el futuro...
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

    controller = Controller(800, 600, "Auxiliar 2")
    controller.set_exclusive_mouse(True)

    vert_source = """
    #version 330

    in vec3 position;
    in vec2 texCoord; 

    out vec2 fragTexCoord; 

    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);

    void main() {
        fragTexCoord = texCoord;
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """
    frag_source = """
    #version 330
    in vec2 fragTexCoord;

    uniform sampler2D u_texture;

    out vec4 outColor;

    void main() {
        // Aqui la función "texture" recibe una imagen almacenada, en este caso, en u_texture
        // y una coordenada, almacenada en fragTexCoord
        // Con esa información entrega el color que hay en la coordenada fragTexCoord de la imagen.
        outColor = texture(u_texture, fragTexCoord);



        // Descomentar lo siguiente para la solución

        //vec4 tempColor = texture(u_texture, fragTexCoord);
        //outColor = vec4(tempColor.x, 0, tempColor.z, 1);
        //outColor = vec4(0, tempColor.y, tempColor.z, 1);
    }
    """

    # Definimos el pipeline usando los shaders
    pipeline = ShaderProgram(Shader(vert_source, "vertex"), Shader(frag_source, "fragment"))
    
    # Esta variable almacena el camino a la carpeta actual
    root = os.path.dirname(__file__)

    # Se crea una cámara usando la clase definida más arriba
    cam = MyCam([0, 0, 0.5])

    # Esto es un grafo de escena, también lo veremos más adelante
    world = SceneGraph(cam)

    # Definimos un cuadrado, atención a lo que hay en el archivo shapes, lo pueden usar!
    cuadrado = Model(shapes.Square["position"], shapes.Square["uv"], index_data=shapes.Square["indices"])

    # Creamos una textura con la clase Texture()
    image = Texture(root + "/fiu.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST)
    
    # Agregamos nuestro objeto al grafo de escena, lleva un nombre, su geometría y su textura
    world.add_node("fondo", mesh=cuadrado, texture=image, pipeline=pipeline)

    # Aqui podríamos cambiar su posicion u otros atributos...
    world["fondo"]["position"] = [0, 0, 0]
    world["fondo"]["scale"] = [1, 1, 1]


    # Función on_draw() realiza cada render
    @controller.event
    def on_draw():
        controller.clear()
        
        # Limpia pantalla y la coloca en el color [1, 1, 1, 1] = blanco
        glClearColor(1,1,1,1)

        # Dibuja todos los objetos que hay en el grafo de escena
        world.draw()

    # A continuación, este es el código que gestiona el control de la cámara. Más adelante lo estudiaremos
    #-------------------------------------------
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

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0
    #-------------------------------------------

    # Se utiliza esta función para actualizar los objetos en pantalla, NO para dibujarlos SOLO actualizarlos
    # Esto podría significar actualizar su posición, rotación, color, etc...
    def update(dt):
        # El método update() del grafo de escena, actualiza las posiciones y transformaciones de cada objeto
        # Más adelante veremos realmente que sucede por debajo
        world.update()

        # Este método actualiza la posicion y orientación de la cámara en cada frame
        cam.time_update(dt)

        # USamos esta variable para almacenar el tiempo transcurrido
        controller.time += dt

    clock.schedule_interval(update,1/60)
    run()