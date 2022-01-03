import random
import tkinter as tk
from tkinter import font as tkfont
import numpy as np

#################################################################
##
##  variables du jeu 

# 0 vide
# 1 mur
# 2 maison des fantomes (ils peuvent circuler mais pas pacman)

TBL = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
       [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
       [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
       [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
       [1, 0, 1, 0, 1, 1, 0, 1, 1, 2, 2, 1, 1, 0, 1, 1, 0, 1, 0, 1],
       [1, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 1],
       [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
       [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
       [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
       [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
       [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

TBL = np.array(TBL, dtype=np.int32)
TBL = TBL.transpose()  ## ainsi, on peut écrire TBL[x][y]

ZOOM = 40  # taille d'une case en pixels
EPAISS = 8  # epaisseur des murs bleus en pixels
HAUTEUR = TBL.shape[1]
LARGEUR = TBL.shape[0]

screeenWidth = (LARGEUR + 1) * ZOOM
screenHeight = (HAUTEUR + 2) * ZOOM

###########################################################################################

# création de la fenetre principale  -- NE PAS TOUCHER

Window = tk.Tk()
Window.geometry(str(screeenWidth) + "x" + str(screenHeight))  # taille de la fenetre
Window.title("ESIEE - PACMAN")

# création de la frame principale stockant plusieurs pages

F = tk.Frame(Window)
F.pack(side="top", fill="both", expand=True)
F.grid_rowconfigure(0, weight=1)
F.grid_columnconfigure(0, weight=1)

# gestion des différentes pages

ListePages = {}
PageActive = 0


def CreerUnePage(id):
    Frame = tk.Frame(F)
    ListePages[id] = Frame
    Frame.grid(row=0, column=0, sticky="nsew")
    return Frame


def AfficherPage(id):
    global PageActive
    PageActive = id
    ListePages[id].tkraise()


def WindowAnim():
    MainLoop()
    Window.after(500, WindowAnim)


Window.after(100, WindowAnim)

# Ressources

PoliceTexte = tkfont.Font(family='Arial', size=22, weight="bold", slant="italic")

# création de la zone de dessin

Frame1 = CreerUnePage(0)

canvas = tk.Canvas(Frame1, width=screeenWidth, height=screenHeight)
canvas.place(x=0, y=0)
canvas.configure(background='black')


################################################################################
#
# placements des pacgums et des fantomes

def PlacementsGUM():  # placements des pacgums
    GUM = np.zeros(TBL.shape)

    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            if (TBL[x][y] == 0):
                GUM[x][y] = 1
    return GUM


GUM = PlacementsGUM()

PacManPos = [5, 5]

Ghosts = []
Ghosts.append([LARGEUR // 2, HAUTEUR // 2, "pink", "UP"])
Ghosts.append([LARGEUR // 2, HAUTEUR // 2, "orange", "DOWN"])
Ghosts.append([LARGEUR // 2, HAUTEUR // 2, "cyan", "LEFT"])
Ghosts.append([LARGEUR // 2, HAUTEUR // 2, "red", "RIGHT"])


################################################################################
#
# Règle de jeu et création de la carte des distances
def IndexInList(liste, index) -> bool:
    return index < len(liste)


def InitGrille() -> None:
    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            valTBL = TBL[x][y]
            # 0 vide
            # 1 mur
            # 2 maison des fantomes (ils peuvent circuler mais pas pacman)
            if valTBL != 1:
                if GUM[x][y] == 0:
                    Grille[x][y] = 100
                else:
                    Grille[x][y] = 0
            else:
                Grille[x][y] = 999


def GetMinValueAroundACase(x, y) -> int:
    """
    Retourne les valeurs minimum des cases voisine à partir de la position de la case passée paramètre
    :param x: La position en Largeur
    :param y: La position en Hauteur
    :return: Le minimum des cases voisines, s'il ne trouve pas l'indice il retourne 999 (valeur des murs)
    """
    defaultValueNotFound = 999

    valCase1 = Grille[x + 1][y] if IndexInList(Grille, x + 1) else defaultValueNotFound
    valCase2 = Grille[x - 1][y] if IndexInList(Grille, x - 1) else defaultValueNotFound
    valCase3 = Grille[x][y + 1] if IndexInList(Grille[x], y + 1) else defaultValueNotFound
    valCase4 = Grille[x][y - 1] if IndexInList(Grille[x], y - 1) else defaultValueNotFound

    return min(valCase1, valCase2, valCase3, valCase4)


def CalculerValeurCasesGrille() -> bool:
    isMiseAjour = False

    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            valTBL = TBL[x][y]

            if valTBL == 1 or Grille[x][y] < 0:
                continue

            # Stocke les valeurs de la case courante et voisines
            valCurrentCase = Grille[x][y]
            valMin = GetMinValueAroundACase(x, y) + 1

            if valMin < valCurrentCase:
                Grille[x][y] = valMin
                isMiseAjour = True

    return isMiseAjour


def UpdateGrille() -> None:
    InitGrille()
    GrilleIsMiseAJour = CalculerValeurCasesGrille()

    while GrilleIsMiseAJour:
        GrilleIsMiseAJour = CalculerValeurCasesGrille()


Score = 0
Grille = np.zeros(TBL.shape)
InitGrille()


#################################################################
##
##  FNT AFFICHAGE


def To(coord):
    return coord * ZOOM + ZOOM


# dessine l'ensemble des éléments du jeu par dessus le décor

anim_bouche = 0
animPacman = [5, 10, 15, 10, 5]


def Affiche():
    global anim_bouche, Score

    def CreateCircle(x, y, r, coul):
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=coul, width=0)

    canvas.delete("all")

    # murs

    for x in range(LARGEUR - 1):
        for y in range(HAUTEUR):
            if (TBL[x][y] == 1 and TBL[x + 1][y] == 1):
                xx = To(x)
                xxx = To(x + 1)
                yy = To(y)
                canvas.create_line(xx, yy, xxx, yy, width=EPAISS, fill="blue")

    for x in range(LARGEUR):
        for y in range(HAUTEUR - 1):
            if (TBL[x][y] == 1 and TBL[x][y + 1] == 1):
                xx = To(x)
                yy = To(y)
                yyy = To(y + 1)
                canvas.create_line(xx, yy, xx, yyy, width=EPAISS, fill="blue")

    # pacgum
    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            if (GUM[x][y] == 1):
                xx = To(x)
                yy = To(y)
                e = 5
                canvas.create_oval(xx - e, yy - e, xx + e, yy + e, fill="orange")

    # extra info
    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            xx = To(x)
            yy = To(y) + 10
            txt = "∞"
            canvas.create_text(xx, yy, text=txt, fill="white", font=("Purisa", 8))

    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            if Grille[x][y] <= 100:
                xx = To(x)
                yy = To(y) + 10
                txt = Grille[x][y]
                canvas.create_text(xx, yy, text=txt, fill="RED", font=("Purisa", 8))

    # dessine pacman
    xx = To(PacManPos[0])
    yy = To(PacManPos[1])
    e = 20
    anim_bouche = (anim_bouche + 1) % len(animPacman)
    ouv_bouche = animPacman[anim_bouche]
    tour = 360 - 2 * ouv_bouche
    canvas.create_oval(xx - e, yy - e, xx + e, yy + e, fill="yellow")
    canvas.create_polygon(xx, yy, xx + e, yy + ouv_bouche, xx + e, yy - ouv_bouche, fill="black")  # bouche

    # dessine les fantomes
    dec = -3
    for P in Ghosts:
        xx = To(P[0])
        yy = To(P[1])
        e = 16

        coul = P[2]
        # corps du fantome
        CreateCircle(dec + xx, dec + yy - e + 6, e, coul)
        canvas.create_rectangle(dec + xx - e, dec + yy - e, dec + xx + e + 1, dec + yy + e, fill=coul, width=0)

        # oeil gauche
        CreateCircle(dec + xx - 7, dec + yy - 8, 5, "white")
        CreateCircle(dec + xx - 7, dec + yy - 8, 3, "black")

        # oeil droit
        CreateCircle(dec + xx + 7, dec + yy - 8, 5, "white")
        CreateCircle(dec + xx + 7, dec + yy - 8, 3, "black")

        dec += 3

    # texte blabla

    canvas.create_text(screeenWidth // 2, screenHeight - 50, text="Hello", fill="yellow", font=PoliceTexte)
    canvas.create_text(screeenWidth // 2, 15, text="Score " + str(Score), fill="yellow", font=PoliceTexte)


#################################################################
##
##  IA RANDOM


def PacManPossibleMove():
    L = []
    x, y = PacManPos

    valMin = GetMinValueAroundACase(x, y)

    if TBL[x][y - 1] == 0 and Grille[x][y - 1] == valMin: L.append((0, -1))
    if TBL[x][y + 1] == 0 and Grille[x][y + 1] == valMin: L.append((0, 1))
    if TBL[x + 1][y] == 0 and Grille[x + 1][y] == valMin: L.append((1, 0))
    if TBL[x - 1][y] == 0 and Grille[x - 1][y] == valMin: L.append((-1, 0))
    return L


def NbCheminVide(x, y) -> int:
    nbCheminVide = 0
    if TBL[x][y - 1] == 1: nbCheminVide += 1
    if TBL[x][y + 1] == 1: nbCheminVide += 1
    if TBL[x + 1][y] == 1: nbCheminVide += 1
    if TBL[x - 1][y] == 1: nbCheminVide += 1
    return nbCheminVide


def IsCroisement(x, y) -> bool:
    return NbCheminVide(x, y) >= 3


def IsTournant(x, y) -> bool:
    return NbCheminVide(x, y) == 2


def GhostsPossibleMove(x, y):
    L = []
    if (TBL[x][y - 1] == 2): L.append((0, -1))
    if (TBL[x][y + 1] == 2): L.append((0, 1))
    if (TBL[x + 1][y] == 2): L.append((1, 0))
    if (TBL[x - 1][y] == 2): L.append((-1, 0))
    return L


def GhostMove(x, y, direction):
    L = []
    if IsCroisement(x, y) or IsTournant(x, y):
        LGhostPossibleMove = GhostsPossibleMove(x, y)
        choix = random.randrange(len(LGhostPossibleMove))

        return LGhostPossibleMove[choix]

    if direction == "UP":
        L.append((0, -1))
    elif direction == "DOWN":
        L.append((0, 1))
    elif direction == "RIGHT":
        L.append((1, 0))
    elif direction == "LEFT":
        L.append((-1, 0))
    return L


def IA():
    global PacManPos, Ghosts, Score

    # deplacement Pacman
    L = PacManPossibleMove()
    choix = random.randrange(len(L))
    PacManPos[0] += L[choix][0]
    PacManPos[1] += L[choix][1]

    # PACMAN EAT GUM
    if GUM[PacManPos[0]][PacManPos[1]] == 1:
        Score += 1
        GUM[PacManPos[0]][PacManPos[1]] = 0

    # deplacement Fantome
    for F in Ghosts:
        L = GhostMove(F[0], F[1], F[3])
        choix = random.randrange(len(L))
        val = L[0][0]
        F[0] += val
        #F[1] += L[0][1]

    UpdateGrille()


#################################################################
##
##   GAME LOOP

def MainLoop():
    IA()
    Affiche()


###########################################:
#  demarrage de la fenetre - ne pas toucher

AfficherPage(0)
Window.mainloop()
