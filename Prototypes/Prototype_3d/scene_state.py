plane_vertices = None
spacing = None

def set_plane_data(vertices, spc):
    global plane_vertices, spacing
    plane_vertices = vertices
    spacing = spc

def calculate_deformed_volume():
    if plane_vertices is None or spacing is None:
        return 0.0

    total_volume = 0.0
    for i in range(plane_vertices.shape[0]):
        for j in range(plane_vertices.shape[1]):
            height = plane_vertices[i][j]
            if height < 0:
                total_volume += abs(height) * (spacing ** 2)
    return total_volume
