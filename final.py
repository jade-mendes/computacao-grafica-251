import colorsys
import math
import pygame

LARGURA, ALTURA = 800, 800

# --------- OBJETO 1: CILINDRO SEM BASE INFERIOR ---------
def cria_cilindro(raio=1.5, altura=5.37, segmentos=128):
    vertices = []
    faces = []

    for i in range(segmentos):
        ang = 2 * math.pi * i / segmentos
        x = raio * math.cos(ang)
        y = raio * math.sin(ang)
        vertices.append((x, y, 0))           # base inferior
        vertices.append((x, y, altura))      # base superior

    # Não adiciona a base inferior

    faces.append([i*2 + 1 for i in range(segmentos)])  # apenas base superior

    for i in range(segmentos):
        base1 = (i * 2) % (segmentos * 2)
        base2 = ((i + 1) * 2) % (segmentos * 2)
        topo1 = base1 + 1
        topo2 = base2 + 1
        faces.append([base1, base2, topo2, topo1])  # lateral

    return vertices, faces

vertices1_raw, faces1 = cria_cilindro()
# Aplica deslocamento para coincidir com posição original
def centraliza(vertices):
    cx = sum(x for x, _, _ in vertices) / len(vertices)
    cy = sum(y for _, y, _ in vertices) / len(vertices)
    cz = sum(z for _, _, z in vertices) / len(vertices)
    return [(x - cx, y - cy, z - cz) for x, y, z in vertices]

def transforma(vertices, posicao):
    vc = centraliza(vertices)
    return [(x + posicao[0], y + posicao[1], z + posicao[2]) for x, y, z in vc]

vertices1 = transforma(vertices1_raw, (-3, 0, 0))

# --------- OBJETO 2: BLOCO ---------
vertices2 = [
    (3,0,0), (3,4,0), (0,4,0), (0,0,0),
    (2,1,1), (2,3,1), (1,3,1), (1,1,1)
]

faces2 = [
    [1,0,4,5], [1,2,6,5], [2,3,7,6],
    [0,3,7,4], [1,2,3,0], [5,6,7,4]
]

# --------- COR FIXA ---------
hue1 = 120  # verde
hue2 = 315  # rosa

# --------- FUNÇÕES VETORIAIS ---------
def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )
def normalize(v):
    norm = math.sqrt(dot(v, v))
    return (v[0]/norm, v[1]/norm, v[2]/norm) if norm != 0 else (0, 0, 0)

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

# --------- ILUMINAÇÃO ---------
light_dir = normalize((-2, -1, -3))

# --------- PROJEÇÃO ---------
def projeta_isometrica(p):
    x, y, z = p
    ang = math.radians(30)
    x_iso = (x - y) * math.cos(ang)
    y_iso = (x + y) * math.sin(ang) - z
    escala = 60
    offset = (LARGURA // 2, ALTURA // 2)
    return (int(x_iso * escala + offset[0]), int(y_iso * escala + offset[1]))

# --------- PRÉ-PROCESSAMENTO ---------
v1 = vertices1
v2 = transforma(vertices2, (3, 0, 0))
todos_vertices = v1 + v2
vertices_proj = [projeta_isometrica(v) for v in todos_vertices]

faces_idx1 = [(face, hue1) for face in faces1]
faces_idx2 = [([idx + len(v1) for idx in face], hue2) for face in faces2]
todas_faces = faces_idx1 + faces_idx2

# --------- PYGAME SETUP ---------
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Cilindro sem base inferior")
clock = pygame.time.Clock()
running = True

while running:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

    tela.fill((0, 0, 0))
    faces_para_desenhar = []

    for face, hue in todas_faces:
        p0, p1, p2 = todos_vertices[face[0]], todos_vertices[face[1]], todos_vertices[face[2]]
        v1f = sub(p1, p0)
        v2f = sub(p2, p0)
        normal = normalize(cross(v1f, v2f))

        intensidade = dot(normal, light_dir)

        saturacao = 0.5 + 0.5 * abs(intensidade)
        brilho = 0.3 + 0.7 * abs(intensidade)
        cor = hsv_to_rgb(hue, saturacao, brilho)

        proj_pontos = [vertices_proj[i] for i in face]
        profundidade_média = sum(p[1] for p in proj_pontos) / len(proj_pontos)

        faces_para_desenhar.append((profundidade_média, proj_pontos, cor))

    faces_para_desenhar.sort(key=lambda f: f[0], reverse=True)

    for _, pontos, cor in faces_para_desenhar:
        pygame.draw.polygon(tela, cor, pontos)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
