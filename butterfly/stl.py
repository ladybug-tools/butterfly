import os

class BFGeometryMesh:
    """
    ButterFly mesh

    Attributes:
        vertices: A list of tuples with 3 values (x,y,z) for each vertice
        faces: A list of tuples or list for order of vertices for each mesh face
        faceNormals: A list of tuples with 3 values (x,y,z) for each normal
        faceNames: A list of names as string. If names left empty, it will be assigned automatically

    Usage:
        vertices = [(0,0,0),(0,10,0),(10,10,0),(10,0,0)]
        faces = [(0, 1, 2, 3)]
        normals = [(0,0,1)]
        GMesh = BFGeometryMesh(vertices, faces, normals)
    """

    def __init__(self, vertices, faces, faceNormals, faceNames = None):
        self.faces = faces
        self.vertices = vertices
        self.normals = faceNormals

        if len(self.faces)!= len(self.normals):
            raise Exception("Number of mesh faces should be equal to number of normals")

        if not faceNames:
            self.faceNames = map(str, range(len(self.faces)))
        else:
            assert len(faces) == len(faceNames)
            self.faceNames = faceNames

    @staticmethod
    def isBFGeometryMesh():
        return True

class STLMesh:
    """
    ButterFly STLMesh

    Attributes:
        BFGeometryMeshes: A list of Butterfly geometry meshes

    Usage:
        stl = STLMesh(BFGMeshes)
        stl.writeToFile(filepath, filename)
    """

    def __init__(self, BFGeometryMeshes):
        self.meshes = BFGeometryMeshes
        self.__checkInputMeshes()

    def __checkInputMeshes(self):
        for mesh in self.meshes:
            try:
                mesh.isBFGeometryMesh()
            except:
                return False

    def writeToFile(self, filepath, filename):

        # checking file name and file path
        if not filename.lower().endswith('.stl'):
            filename += '.stl'

        if not os.path.isdir(filepath):
            os.mkdir(filepath)

        stlFilePath = os.path.join(filepath, filename)

        stlFile = []

        for mesh in self.meshes:

            for meshCount, meshFace in enumerate(mesh.faces):

                vertices = [mesh.vertices[i] for i in meshFace]
                faceNormal = mesh.normals[meshCount]
                faceName = mesh.faceNames[meshCount]

                # generate stl string
                solidStr = 'solid ' + faceName
                stlFile.append(solidStr)

                # handle quad mesh faces
                if len(vertices) == 4:
                    verList = [vertices[:3], [vertices[0], vertices[2], vertices[3]]]
                else:
                    verList = [vertices]

                for coorList in verList:
                    #   facet normal 0.400645 -0.916233 0.0
                    stlFile.append('  facet normal %f %f %f'%(faceNormal[0], \
                                                              faceNormal[1], \
                                                              faceNormal[2]))

                    stlFile.append('  \touter loop')

                    #   vertex 9.59792 -22.1636 4.20010
                    #   vertex 7.65496 -23.0133 4.20010
                    #   vertex 7.65496 -23.0133 2.10005
                    for ver in coorList:
                        stlFile.append('   \t   vertex %f %f %f'%(ver[0], \
                                                                  ver[1], \
                                                                  ver[2]))

                    stlFile.append('  \tendloop')
                    stlFile.append('  endfacet')

                # endsolid patch1_1
                stlFile.append('end' + solidStr)

        # write it to a file
        with open(stlFilePath, 'w') as stloutfile:
            stloutfile.write('\n'.join(stlFile))

class BFPointMesh:
    """
    ButterFly point mesh

    Attributes:
        vertices: A list of list of tuples with 3 values (x,y,z) for each vertice
        faceNormals: A list of tuples with 3 values (x,y,z) for each normal
        faceNames: A list of names as string. If names left empty, it will be assigned automatically

    Usage:
        vertices = [[(0,0,0),(0,10,0),(10,10,0),(10,0,0)]]
        normals = [(0,0,1)]
        GMesh = BFPointMesh(vertices, normals)
    """

    def __init__(self, vertices, faceNormals, faceNames = None):
        self.vertices = vertices
        self.normals = faceNormals

        if len(self.vertices)!= len(self.normals):
            raise Exception("Number of mesh faces should be equal to number of normals")

        if not faceNames:
            self.faceNames = map(str, range(len(self.vertices)))
        else:
            assert len(self.vertices) == len(faceNames)
            self.faceNames = faceNames

    @staticmethod
    def isBFPointMesh():
        return True

class STLMeshFromPointMesh:
    """
    ButterFly STLMesh from Point Mesh

    Attributes:
        BFPointMeshes: A list of Butterfly point meshes

    Usage:
        stl = STLMeshFromPointMesh(BFPointMeshes)
        stl.writeToFile(filepath, filename)
    """

    def __init__(self, BFPointMeshes):
        self.meshes = BFPointMeshes
        self.__checkInputMeshes()

    def __checkInputMeshes(self):
        for mesh in self.meshes:
            try:
                mesh.isBFPointMesh()
            except:
                return False

    def writeToFile(self, filepath, filename):

        # checking file name and file path
        if not filename.lower().endswith('.stl'):
            filename += '.stl'

        if not os.path.isdir(filepath):
            os.mkdir(filepath)

        stlFilePath = os.path.join(filepath, filename)

        stlFile = []

        for mesh in self.meshes:

            for meshCount, vertices in enumerate(mesh.vertices):

                faceNormal = mesh.normals[meshCount]
                faceName = mesh.faceNames[meshCount]

                # generate stl string
                solidStr = 'solid ' + faceName
                stlFile.append(solidStr)

                # handle quad mesh faces
                if len(vertices) == 4:
                    verList = [vertices[:3], [vertices[0], vertices[2], vertices[3]]]
                else:
                    verList = [vertices]

                for coorList in verList:
                    #   facet normal 0.400645 -0.916233 0.0
                    stlFile.append('  facet normal %f %f %f'%(faceNormal[0], \
                                                              faceNormal[1], \
                                                              faceNormal[2]))

                    stlFile.append('  \touter loop')

                    #   vertex 9.59792 -22.1636 4.20010
                    #   vertex 7.65496 -23.0133 4.20010
                    #   vertex 7.65496 -23.0133 2.10005
                    for ver in coorList:
                        stlFile.append('   \t   vertex %f %f %f'%(ver[0], \
                                                                  ver[1], \
                                                                  ver[2]))

                    stlFile.append('  \tendloop')
                    stlFile.append('  endfacet')

                # endsolid patch1_1
                stlFile.append('end' + solidStr)

        # write it to a file
        with open(stlFilePath, 'w') as stloutfile:
            stloutfile.write('\n'.join(stlFile))
