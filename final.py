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

def centraliza(vertices):
    cx = sum(x for x, _, _ in vertices) / len(vertices)
    cy = sum(y for _, y, _ in vertices) / len(vertices)
    cz = sum(z for _, _, z in vertices) / len(vertices)
    return [(x - cx, y - cy, z - cz) for x, y, z in vertices]

def transforma(vertices, posicao):
    vertices_central = centraliza(vertices)
    return [(x + posicao[0], y + posicao[1], z + posicao[2]) for x, y, z in vertices_central]

# --------- OBJETO 1 ---------
vertices1 = [
    (3, 0, 0), (3, 4, 0), (0, 4, 0), (0, 0, 0),
    (2, 1, 1), (2, 3, 1), (1, 3, 1), (1, 1, 1)
]
faces1 = [
    [1, 0, 4, 5],
    [1, 2, 6, 5],
    [2, 3, 7, 6],
    [0, 3, 7, 4],
    [1, 2, 3, 0],
    [5, 6, 7, 4]
]

# --------- PARTE SUPERIOR DO OBJETO 2 ---------
vertices_topo = [
    (0.5,1,4.5),  # 0
    (0.5,1.5,4.5),  # 1
    (2.5,1,4.5),  # 2
    (2.5,1.5,4.5),  # 3
    (1,1,5.37),  # 4
    (1,1.5,5.37),  # 5
    (2,1,3.63),  # 6
    (2,1.5,3.63),  # 7
    (1.5,1,0),  # 8
    (1.5,1.5,0),  # 9
    (1.75,1,0),  # 10
    (1.75,1.5,0)  # 11
]

faces_topo = [
    [6,7,11,10],      # F, F', H', H
    [2,3,1,0],        # D, D', C', C
    [0,1,5,4],        # C, C', E', E
    [4,5,3,2],        # E, E', D', D
    [1,5,3,7],        # C', E', D', F'
    [0,4,2,6],        # C, E, D, F
]

# --------- BASE CILÍNDRICA ---------
def cria_base_cilindrica(z_base, z_topo, centro_x, centro_y, raio, segmentos):
    vertices = []
    faces = []

    for i in range(segmentos):
        ang = 2 * math.pi * i / segmentos
        x = centro_x + raio * math.cos(ang)
        y = centro_y + raio * math.sin(ang)
        vertices.append((x, y, z_base))  # base
    for i in range(segmentos):
        ang = 2 * math.pi * i / segmentos
        x = centro_x + raio * math.cos(ang)
        y = centro_y + raio * math.sin(ang)
        vertices.append((x, y, z_topo))  # topo

    # Laterais
    for i in range(segmentos):
        a = i
        b = (i + 1) % segmentos
        c = (i + 1) % segmentos + segmentos
        d = i + segmentos
        faces.append([a, b, c, d])

    # Base inferior
    faces.append([i for i in range(segmentos)][::-1])
    return vertices, faces

vertices_cilindro, faces_cilindro = cria_base_cilindrica(
    z_base=0, z_topo=4.0,
    centro_x=1.5, centro_y=1.25,
    raio=0.5, segmentos=64
)

# --------- JUNÇÃO DO CILINDRO + TOPO ---------
offset = len(vertices_cilindro)
vertices2 = vertices_cilindro + vertices_topo
faces2 = faces_cilindro + [[offset + i for i in face] for face in faces_topo]

# --------- CONFIGURAÇÕES PYGAME ---------
LARGURA, ALTURA = 800, 800
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
