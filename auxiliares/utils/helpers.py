import numpy as np
import trimesh as tm
from OpenGL import GL
import utils.transformations as tr
import networkx as nx


# Clase Model() nos ayuda a transformar las figuras de forma mas facil
# Se inicializa con las posiciones de los vertices, los colores de los vertices y la index_data si es que
# tenemos una figura con vertices indexados
class Model():
    def __init__(self, position_data, index_data=None):
        self.position_data = position_data

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

    def init_gpu_data(self, pipeline):
        self.pipeline = pipeline
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(
                len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(
                len(self.position_data) // 3, GL.GL_TRIANGLES)

        self.gpu_data.position[:] = self.position_data

    def draw(self, mode=GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)


# La clase Mesh(Model) es un Model pero con funciones extra,
# Nos permite pasar un mesh hecho en algun software de modelado a OpenGL
# Recibe el path hacia el file, y un color base opcional
class Mesh(Model):
    def __init__(self, asset_path):
        mesh_data = tm.load(asset_path)
        mesh_scale = tr.uniformScale(2.0 / mesh_data.scale)
        mesh_translate = tr.translate(*-mesh_data.centroid)
        mesh_data.apply_transform(mesh_scale @ mesh_translate)
        vertex_data = tm.rendering.mesh_to_vertexlist(mesh_data)
        indices = vertex_data[3]
        positions = vertex_data[4][1]

        super().__init__(positions, indices)


class SceneGraph():
    def __init__(self, camera=None):
        self.graph = nx.DiGraph(root="root")
        self.add_node("root")
        self.camera = camera

    def add_node(self,
                 name,
                 attach_to=None,
                 mesh=None,
                 color=[1, 1, 1],
                 transform=tr.identity(),
                 position=[0, 0, 0],
                 rotation=[0, 0, 0],
                 scale=[1, 1, 1],
                 mode=GL.GL_TRIANGLES):
        self.graph.add_node(
            name,
            mesh=mesh,
            color=color,
            transform=transform,
            position=np.array(position, dtype=np.float32),
            rotation=np.array(rotation, dtype=np.float32),
            scale=np.array(scale, dtype=np.float32),
            mode=mode)
        if attach_to is None:
            attach_to = "root"

        self.graph.add_edge(attach_to, name)

    def __getitem__(self, name):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        return self.graph.nodes[name]

    def __setitem__(self, name, value):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        self.graph.nodes[name] = value

    def get_transform(self, node):
        node = self.graph.nodes[node]
        transform = node["transform"]
        translation_matrix = tr.translate(
            node["position"][0], node["position"][1], node["position"][2])
        rotation_matrix = tr.rotationX(node["rotation"][0]) @ tr.rotationY(
            node["rotation"][1]) @ tr.rotationZ(node["rotation"][2])
        scale_matrix = tr.scale(
            node["scale"][0], node["scale"][1], node["scale"][2])
        return transform @ translation_matrix @ rotation_matrix @ scale_matrix

    def draw(self):
        root_key = self.graph.graph["root"]
        edges = list(nx.edge_dfs(self.graph, source=root_key))
        transformations = {root_key: self.get_transform(root_key)}

        for src, dst in edges:
            current_node = self.graph.nodes[dst]

            if not dst in transformations:
                transformations[dst] = transformations[src] @ self.get_transform(
                    dst)

            if current_node["mesh"] is not None:
                current_pipeline = current_node["mesh"].pipeline
                current_pipeline.use()

                if self.camera is not None:
                    if "u_view" in current_pipeline.uniforms:
                        current_pipeline["u_view"] = self.camera.get_view()

                    if "u_projection" in current_pipeline.uniforms:
                        current_pipeline["u_projection"] = self.camera.get_projection(
                        )

                current_pipeline["u_transform"] = np.reshape(
                    transformations[dst], (16, 1), order="F")

                if "u_color" in current_pipeline.uniforms:
                    current_pipeline["u_color"] = np.array(
                        current_node["color"], dtype=np.float32)
                current_node["mesh"].draw(current_node["mode"])


class Camera():
    def __init__(self, width, height, camera_type="perspective"):
        self.position = np.array([1, 0, 0], dtype=np.float32)
        self.focus = np.array([0, 0, 0], dtype=np.float32)
        self.type = camera_type
        self.width = width
        self.height = height

    def update(self):
        pass

    def get_view(self):
        lookAt_matrix = tr.lookAt(
            self.position, self.focus, np.array([0, 1, 0], dtype=np.float32))
        return np.reshape(lookAt_matrix, (16, 1), order="F")

    def get_projection(self):
        if self.type == "perspective":
            perspective_matrix = tr.perspective(
                90, self.width / self.height, 0.01, 100)
        elif self.type == "orthographic":
            depth = self.position - self.focus
            depth = np.linalg.norm(depth)
            perspective_matrix = tr.ortho(-(self.width/self.height) * depth,
                                          (self.width/self.height) * depth, -1 * depth, 1 * depth, 0.01, 100)
        return np.reshape(perspective_matrix, (16, 1), order="F")

    def resize(self, width, height):
        self.width = width
        self.height = height


class OrbitCamera(Camera):
    def __init__(self, distance, width, height, camera_type="perspective"):
        super().__init__(width, height, camera_type)
        self.distance = distance
        self.phi = 0
        self.theta = np.pi / 2
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distance * \
            np.sin(self.theta) * np.sin(self.phi)
        self.position[1] = self.distance * np.cos(self.theta)
        self.position[2] = self.distance * \
            np.sin(self.theta) * np.cos(self.phi)
