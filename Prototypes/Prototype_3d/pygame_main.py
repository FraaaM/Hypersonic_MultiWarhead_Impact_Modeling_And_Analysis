import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit, glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18
import numpy as np
import tkinter as tk
from shared_params import shared_settings

import results_window
import settings_window

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 30
BUTTON_PADDING = 10

grid_size = 70
spacing = 0.4
plane_vertices = np.zeros((grid_size, grid_size), dtype=np.float32)

rotation = [-40, 0]
dragging = False
last_mouse_pos = (0, 0)
camera_distance = -20

last_intersection = (0.0, 0.0, 0.0)

start_rotation = [-40, 0]
start_camera_distance = -20

reset_mode = False
reset_progress = 0.0
RESET_SPEED = 2.0

def init_text():
    glutInit()

def draw_text(x, y, text):
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def draw_button(x, y, w, h, label, offset_x=0):
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

    text_width = len(label) * 9
    text_height = 18
    tx = x + (w - text_width) / 2 + offset_x
    ty = y + (h - text_height) / 2

    glColor3f(1.0, 1.0, 1.0)
    draw_text(tx, ty, label)

def draw_plane():
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    for x in range(grid_size - 1):
        for y in range(grid_size - 1):
            glBegin(GL_QUADS)
            for dx, dy in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                i = x + dx
                j = y + dy
                px = (i - grid_size / 2) * spacing
                py = (j - grid_size / 2) * spacing
                pz = plane_vertices[i][j]

                if pz >= 0.0:
                    glColor3f(0.5, 0.5, 0.5)
                else:
                    depth = abs(pz)
                    if depth <= 3:
                        r, g, b = 1.0, 1.0, 0.0
                    elif 3 < depth <= 5:
                        r, g, b = 1.0, 0.5, 0.0
                    else:
                        r, g, b = 1.0, 0.0, 0.0
                    glColor3f(r, g, b)

                glVertex3f(px, py, pz)
            glEnd()

    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glLineWidth(1.0)
    glColor4f(0.0, 0.0, 0.0, 0.2)
    for x in range(grid_size):
        glBegin(GL_LINE_STRIP)
        for y in range(grid_size):
            px = (x - grid_size / 2) * spacing
            py = (y - grid_size / 2) * spacing
            pz = plane_vertices[x][y]
            glVertex3f(px, py, pz)
        glEnd()
    for y in range(grid_size):
        glBegin(GL_LINE_STRIP)
        for x in range(grid_size):
            px = (x - grid_size / 2) * spacing
            py = (y - grid_size / 2) * spacing
            pz = plane_vertices[x][y]
            glVertex3f(px, py, pz)
        glEnd()
    glDisable(GL_LINE_SMOOTH)

def get_mouse_intersection(mx, my):
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    winX = mx
    winY = viewport[3] - my

    near = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
    far  = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)

    dir_vector = np.subtract(far, near)
    dir_vector /= np.linalg.norm(dir_vector)

    t = -near[2] / dir_vector[2]
    intersection = near + dir_vector * t
    return intersection

def world_to_grid(ix, iy):
    gx = int(round(ix / spacing + grid_size / 2))
    gy = int(round(iy / spacing + grid_size / 2))
    gx = max(0, min(grid_size - 1, gx))
    gy = max(0, min(grid_size - 1, gy))
    return gx, gy

def create_crater(x, y, radius, depth):
    crater_radius = shared_settings["Диаметр кратера (Dₜ), м:"] / 2 / spacing
    crater_depth = shared_settings["Глубина кратера (hₜ), м:"]

    for i in range(grid_size):
        for j in range(grid_size):
            dist = np.hypot(i - x, j - y)
            if dist < crater_radius:
                nd = dist / crater_radius
                deformation = -crater_depth * (1 - nd**2)
                plane_vertices[i][j] += deformation

    solid_radius = shared_settings["Радиус поражённой зоны (rₛ), м:"] / spacing
    solid_depth = shared_settings["Глубина проникновения (hₛ), м:"]

    for i in range(grid_size):
        for j in range(grid_size):
            dist = np.hypot(i - x, j - y)
            if dist < solid_radius:
                nd = dist / solid_radius
                solid_deformation = -solid_depth * (1 - nd**2)
                plane_vertices[i][j] = min(plane_vertices[i][j] + solid_deformation, plane_vertices[i][j])

def draw_mouse_indicator(mouse_pos):
    global last_intersection
    mx, my = mouse_pos
    intersect = get_mouse_intersection(mx, my)
    last_intersection = intersect

    gx, gy = world_to_grid(intersect[0], intersect[1])
    surface_z = plane_vertices[gx][gy]

    glLineWidth(2.5)
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(intersect[0], intersect[1], surface_z)
    glVertex3f(intersect[0], intersect[1], surface_z + 10.0)
    glEnd()

def main():
    global dragging, last_mouse_pos, rotation, camera_distance, reset_mode, reset_progress

    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
    pygame.font.init()
    init_text()

    width, height = 800, 600
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Плоскость")

    results_button_rect = pygame.Rect(width - BUTTON_PADDING - BUTTON_WIDTH, BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT)
    settings_button_rect = pygame.Rect(width - 2*BUTTON_PADDING - 2*BUTTON_WIDTH, BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT)

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    gluPerspective(45, width / height, 0.1, 100.0)
    glTranslatef(0, 0, camera_distance)

    clock = pygame.time.Clock()
    running = True
    settings_win = None

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                if settings_win is not None:
                    try:
                        settings_win.destroy()
                        settings_win = None
                    except tk.TclError:
                        settings_win = None

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if results_button_rect.collidepoint(event.pos):
                        results_window.show_results_window()
                    elif settings_button_rect.collidepoint(event.pos):
                        if settings_win is None or not settings_window.update_settings_window(settings_win):
                            settings_win = settings_window.show_settings_window()
                    else:
                        dragging = True
                        last_mouse_pos = event.pos

                elif event.button == 3:
                    gx, gy = world_to_grid(*last_intersection[:2])
                    create_crater(gx, gy, shared_settings["Диаметр кратера (Dₜ), м:"] / 2, shared_settings["Глубина кратера (hₜ), м:"])

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                rotation[0] += dy
                rotation[1] += dx
                last_mouse_pos = event.pos

            elif event.type == MOUSEWHEEL:
                camera_distance += event.y
                camera_distance = max(-50, min(2, camera_distance))

            elif event.type == KEYDOWN:
                if event.key == K_q:
                    reset_mode = True
                    reset_progress = 0.0

        if reset_mode:
            reset_progress += clock.get_time() / 1000.0 * RESET_SPEED
            t = min(reset_progress, 1.0)
            rotation[0] = (1 - t) * rotation[0] + t * start_rotation[0]
            rotation[1] = (1 - t) * rotation[1] + t * start_rotation[1]
            camera_distance = (1 - t) * camera_distance + t * start_camera_distance
            if t >= 1.0:
                reset_mode = False

        settings_win = settings_window.update_settings_window(settings_win)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(0, 0, camera_distance)
        glRotatef(rotation[0], 1, 0, 0)
        glRotatef(rotation[1], 0, 1, 0)
        draw_plane()
        draw_mouse_indicator(pygame.mouse.get_pos())
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        mx, my = pygame.mouse.get_pos()
        gx, gy = world_to_grid(*last_intersection[:2])
        surface_z = abs(plane_vertices[gx][gy])
        depth_text = f"Depth: {surface_z:.2f}"
        glColor3f(0.0, 0.0, 1.0)
        draw_text(mx + 10, height - my - 10, depth_text)

        ui_y = height - BUTTON_PADDING - BUTTON_HEIGHT
        draw_button(results_button_rect.x, ui_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Results", offset_x=4)
        draw_button(settings_button_rect.x, ui_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Settings", offset_x=1)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()