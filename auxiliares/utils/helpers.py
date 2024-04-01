import numpy as np
import trimesh as tm
from OpenGL import GL
import utils.transformations as tr


# Clase Model() nos ayuda a transformar las figuras de forma mas facil
# Se inicializa con las posiciones de los vertices, los colores de los vertices, un alpha y la index_data si es que
# tenemos una figura con vertices indexados
class Model():

    # Constructor
    def __init__(self, position_data, color_data, alpha, index_data=None):
        vertices = len(color_data)//3
        self.position_data = position_data
        self.color_data = [1]*(vertices*4)
        j = 0
        i = 0
        while i < vertices:
            self.color_data[j] = color_data[i*3]
            self.color_data[j+1] = color_data[i*3+1]
            self.color_data[j+2] = color_data[i*3+2]
            self.color_data[j+3] = alpha
            i += 1
            j += 4

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.rotation = np.array([0, 0, 0], dtype=np.float32)
        self.scale = np.array([1, 1, 1], dtype=np.float32)

    # Crea el vertex_list
    def init_gpu_data(self, pipeline):
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(
                len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(
                len(self.position_data) // 3, GL.GL_TRIANGLES)

        self.gpu_data.position[:] = self.position_data
        self.gpu_data.color[:] = self.color_data

    # Dibuja en pantalla ( queremos llamar a esto en cada refresh )
    def draw(self, mode=GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)

    # Retorna la matriz de transformacion ( vamos a querer usar esto en cada refresh )
    def get_transform(self):
        translation_matrix = tr.translate(
            self.position[0], self.position[1], self.position[2])
        rotation_matrix = tr.rotationX(
            self.rotation[0]) @ tr.rotationY(self.rotation[1]) @ tr.rotationZ(self.rotation[2])
        scale_matrix = tr.scale(self.scale[0], self.scale[1], self.scale[2])
        transformation = translation_matrix @ rotation_matrix @ scale_matrix
        return np.reshape(transformation, (16, 1), order="F")


# La clase Mesh(Model) es un Model pero con funciones extra,
# Nos permite pasar un mesh hecho en algun software de modelado a OpenGL
# Recibe el path hacia el file, y un color base opcional
class Mesh(Model):
    def __init__(self, asset_path, alpha, base_color=None):
        # se carga con trimesh
        mesh_data = tm.load(asset_path)

        # se deja normalito con las transformaciones
        mesh_scale = tr.uniformScale(2.0 / mesh_data.scale)
        mesh_translate = tr.translate(*-mesh_data.centroid)
        mesh_data.apply_transform(mesh_scale @ mesh_translate)
        vertex_data = tm.rendering.mesh_to_vertexlist(mesh_data)
        indices = vertex_data[3]
        positions = vertex_data[4][1]

        # cantidad de vertices
        count = len(positions) // 3

        # asignar colores
        colors = []
        if base_color is None:
            colors = vertex_data[5][1]
        else:
            colors = np.array(base_color*count, dtype=np.float32)

        super().__init__(positions, colors, alpha, indices)
