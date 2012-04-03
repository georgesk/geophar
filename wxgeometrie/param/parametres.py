# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

######################################
#
#    FICHIER DE CONFIGURATION
#
######################################
#
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2010  Nicolas Pourcelot
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
######################################

# Note :
# eviter d'utiliser des listes au maximum, preferer les tuples.
# en effet, il est souvent utile de copier les parametres.
# Mais par defaut, une liste n'est pas reellement copiee (il faut faire l2 = l1[:]).
# Si de plus, on utilise des listes de listes, on a vite fait d'obtenir des bugs etranges...

from locale import getdefaultlocale
from math import pi

python_min = (2, 6) # version minimale requise

# debuguage (affichage des erreurs + diverses infos)
debug = True
# Le logiciel est-il install� ?
# Cela change les r�pertoires par d�faut (session, etc.)
install = False
# affichage ou non des avertissements
warning = debug
verbose = 1 # 0, 1, 2 ou 3
# � terme, verbose=0 doit couper *tous* les messages (pour ne pas parasiter les tests).
# => cr�er une fonction print() personnalis�e.
# Indique si geolib doit afficher les diff�rents messages. Dans certaines consoles (ex: pyshell), cela provoque des comportements ind�sirables.
afficher_messages = True
#TODO: retravailler ces diff�rents param�tres.

fermeture_instantanee = False # Utile en mode d�veloppement

# affichage de la ligne de commande (utile pour le d�veloppement)
ligne_commande = debug

NOMPROG = u"G�ophar"
NOMPROG2 = 'Geophar' # sans accent
GUIlib = 'Qt'
LOGO = '%/images/logo6.png'

version_wxpython = "2.8-unicode"

# Les valeurs sont les noms des paquets sous Debian/Ubuntu.
dependances = {'PyQt4': 'python-qt4', 'matplotlib': 'python-matplotlib', 'numpy': 'python-numpy'}

latex = False
latex_unicode = True # (sera �ventuellement d�sactiv� ult�rieurement, apr�s l'import de wx)

moteur_de_rendu = 'QTAgg' # ou 'QT' pour supprimer l'anti-cr�n�lage

# Permet de tester les styles sous d'autres plateformes.
# Styles possibles: 'Windows', 'Motif', 'CDE', 'Plastique', 'GTK+',
# 'Cleanlooks', 'WindowsXP', 'WindowsVista' et 'Macintosh'.
# NB: Les 3 derniers styles ne sont possible que sur leur plateforme d'origine.
style_Qt = None



# jeu de caract�re � utiliser
encodage = getdefaultlocale()[1] or "utf8"

# Utiliser pysco si disponible (JIT compiler qui acc�l�re le code python)
# True -> tout compiler : psyco.full()
# None -> compilation optimis�e : psyco.profile()
# False -> ne pas essayer d'importer psyco
charger_psyco = False

# Modules activ�s par d�faut
modules_par_defaut = (
    "geometre",
    "traceur",
    "statistiques",
    "calculatrice",
    "probabilites",
    "surfaces",
        )

# Multi-threading pour les macros
# -------------------------------

multi_threading = False

# c'est assez instable...

if multi_threading is None:
    multi_threading = (plateforme == 'Windows') # ca ne marche pas avec le serveur X (sous Linux par ex.)


# Param�tres g�n�raux
# --------------------

utilisateur = "" # nom de l'utilisateur, pour inclure dans les documents cr��s

dimensions_fenetre = (890, 630)
confirmer_quitter = True
nbr_annulations = 50
# Cr�er un fichier .log (conseill�)
historique_log = True
# Modifier ce fichier en temps r�el (peu utile)
historique_log_continu = False
# Enregistrer les messages (notamment d'erreur) dans messages.log
enregistrer_messages = True
# Sauver les pr�f�rences � la fermeture du programme, pour les restaurer au prochain d�marrage
sauver_preferences = True
# Sauver la session en cours � la fermeture du programme, pour la restaurer au prochain d�marrage
sauver_session = True
# Param�tre utilis� essentiellement en interne (quand on lance WxG�ometrie avec l'option --defaut)
charger_preferences = True

# Intervalle de temps (en dizaines de secondes) entre 2 sauvegardes automatiques
sauvegarde_automatique = 2
# (Mettre 0 pour la d�sactiver)

tolerance = 1e-8 # seuil de tol�rance, utilis� en particulier par geolib pour savoir si 2 points sont confondus
# ce param�tre permet un compromis acceptable entre les faux negatifs
# (2 points confondus consid�r�s � tort comme distincts, du fait d'impr�cisions de calculs qui se cumulent)
# et les faux positifs (deux points proches consider�s � tort comme confondus).

# Parametres d'affichage
# ----------------------

orthonorme = False
grille_aimantee = False # force les points � se placer sur le quadrillage

afficher_barre_outils = False
afficher_console_geolib = False
afficher_boutons = True  # Possibilit� de ne pas afficher les boutons, pour obliger � une construction pas � pas.

zoom_texte = 1
zoom_ligne = 1

#constantes
RIEN = 0
NOM = 1
TEXTE = 2
FORMULE = 3
DEBUT = 0
MILIEU = 0.5
FIN = 1
#TODO: supprimer cette section une fois qu'une partie de param sera directement int�gr�e � geolib.

# Styles li�s � la cat�gorie:
styles_de_lignes = ['-', '--', '-.', ':', 'None']
styles_de_points = ['+', 'x', 'o', '.', ',', '1', '2', '3', '4', '<', '>', '^', 'v', 'D', 'H', '_', '|', 'd', 'h', 'p', 's']
styles_de_textes = ["normal", "italic", "oblique"]
styles_de_angles = ['-', '--', '-.', ':', 'steps', 'None']
familles_de_textes = ["sans-serif", "serif", "cursive", "fantasy", "monospace"]
codage_des_lignes = ['', '/', '//', '///', 'x', 'o']
codage_des_angles = ['', '^', ')', '))', ')))', '|', '||', 'x', 'o']

# Enum�re les styles 'variables' :
# - soit parce qu'ils ont des significations assez diff�rentes selon les objets
# - soit parce qu'ils ne peuvent pas prendre les m�mes valeurs suivant les objets
# Ces styles ne seront copi�s d'un objet � l'autre que s'ils appartiennent � la m�me cat�gorie
styles_a_signification_variable = ("style", "codage", "famille", "taille", "angle")

# Ces styles ne seront pas copi�s, quelque soit la cat�gorie de la cible
styles_a_ne_pas_copier = ("categorie", "niveau", "trace", "fixe", "label", "_rayon_", "_k_", "_angle_", "_noms_", "legende")


types_de_hachures = [' ', '/', '//', '\\', '\\\\', '|', '-', '+', 'x', 'o', 'O', '.', '..', '*']
# en r�alit�, on peut aussi les panacher...


defaut_objets = {
    "legende": RIEN,
    "visible": True,
    "label": "",
    "niveau": 0,
    }
widgets = {"bidon":1,
    }
variables = {
    "visible": False,
    }
points = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "+",
    "categorie": "points",
    "taille": 8,
    "visible": True,
    "legende": NOM,
    "niveau": 6,
    "trace": False,
    }
points_deplacables = {
    "couleur": "r",
    "niveau": 10,
    "fixe": False,
    }
segments = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 3,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    }
interpolations = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 3,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    "debut": True,
    "fin": True,
    }
droites = {"couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 2,
    "categorie": "lignes",
    }
courbes = {"couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 2,
    "categorie": "lignes",
    "extremites": True,
    "extremites_cachees": (),
    }
vecteurs = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "taille": 10,
    "visible": True,
    "niveau": 4,
    "categorie": "lignes",
    "angle": 60,
    "position": FIN,
    "double_fleche": False,
    }
axes = {
    "couleur": "k",
    "epaisseur": 1.,
    "style": "-",
    "taille": 10,
    "visible": True,
    "niveau": .1,
    "categorie": "lignes",
    "angle": 60,
    "position": FIN,
    "double_fleche": False,
    }
cercles = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 1,
    "categorie": "lignes",
    }
arcs = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 1,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    }
arcs_orientes = {
    "couleur": "g",
    "epaisseur": 1.,
    "style": "-",
    "taille": 10,
    "visible": True,
    "niveau": 4,
    "categorie": "lignes",
    "angle": 60,
    "position": FIN,
    "double_fleche": False,
    }
polygones = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "alpha": .2,
    "niveau": 0.1,
    "hachures": types_de_hachures[0],
    "categorie": "lignes",
    }
cotes = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "alpha": 1,
    "niveau": 0,
    "categorie": "lignes",
    "codage": codage_des_lignes[0],
    }
polyedres = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "None",
    "visible": True,
    "alpha": .2,
    "niveau": 0,
    "hachures": types_de_hachures[0],
    "categorie": "lignes",
    }
aretes = {
    "couleur": "y",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 0.5,
    "categorie": "lignes",
    }
textes = {
    "couleur": "k",
    "epaisseur": 5, # 1 -> 9
    #"largeur": ("normal", "narrow", "condensed", "wide")[0],  # mal gere par matploltib (version 0.87)
    "taille": 18.,
    "style": "normal",
    "famille": familles_de_textes[1],
    "visible": True,
    "angle": 0,
    "legende": TEXTE,
    "fixe": False,
    "categorie": "textes",
    "niveau": 7,
    "alignement_vertical": "center",
    "alignement_horizontal": "center",
    }
boutons = {
    "couleur": 'k',
    "couleur_fond": (.3, .8, .9),
    "epaisseur": 1,
    "taille": 18.,
    "style": "italic",
    "visible": True,
    "angle": 0,
    "legende": TEXTE,
    "fixe": True,
    "categorie": "widgets",
    "niveau": 10,
    "alignement_vertical": "center",
    "alignement_horizontal": "center",
    "marge": 3,
    }
labels = {
    "couleur": "k",
    "epaisseur": 6, # 1 -> 9
    #"largeur": ("normal", "narrow", "condensed", "wide")[0],  # mal gere par matploltib (version 0.87)
    "taille": 18.,
    "style": "normal",
    "famille": familles_de_textes[1],
    "visible": True,
    "angle": 0,
    "legende": TEXTE,
    "fixe": False,
    "categorie": "textes",
    "niveau": 7,
    "alignement_vertical": "bottom",
    "alignement_horizontal": "left",
    }
angles = {
    "couleur": "b",
    "epaisseur": 1.,
    "style": "-",
    "visible": True,
    "niveau": 5,
    "categorie": "angles",
    "codage": codage_des_angles[0],
    "alpha": .2,
}

# le parametre niveau est utilis� pour d�tecter l'objet sur la feuille :
# en cas de conflit entre deux objets proches, il permet de savoir l'objet � s�lectionner.
# les petits objets (points, ...) doivent �tre au dessus des plus gros, et avoir un niveau sup�rieur.
# Rq: les objets modifiables devraient etre "au dessus" des autres, ind�pendamment de leur taille.
# Attention, ce parametre n'influe pas sur l'affichage des objets (pour cela, c'est le parametre "zorder" de matplotlib)

# le parametre "categorie" indique quelle liste de styles est � appliquer.
# par d�faut, on applique souvent 'styles_de_lignes'.

del NOM, FORMULE, TEXTE, RIEN, DEBUT, MILIEU, FIN



# Options de style pour les objets geometriques :
#   couleur:      str
#   epaisseur:    float
#   taille:       float
#   style:        str
#   visible:      bool
#   fixe:         bool
#   label:        str
#   extra:       dict
# 'extra' est un dictionnaire d'options de matplotlib
# attention, ces options seront appliquees a toutes les composantes (plot, fill, text) de la representation graphique

codage = {"angle": 60, "taille": 6, "rayon": 20}
codage_automatique_angle_droits = True


# taille de differents elements graphiques

taille = {"o" : 3, "(" : 5, ">" : 10, "|" : 8}


# Distance maximale entre une etiquette et son objet associ� :
distance_max_etiquette = 50

# D�SUET :
##chiffres_significatifs = 4 # intervient dans l'affichage des propri�t�s des objets essentiellement.

decimales = 2

# Note: en interne, ce sont toujours les radians qui sont utilis�s.
unite_angle = ("r", "d", "g")[0] # radian, degr� ou grad


liste_axes = (0, 1)
# 0 -> axe des abscisses ;  1 -> axe des ordonnees

afficher_axes = True
afficher_fleches = True # fleches au bout des axes.

# Pour se reperer, deux possibilites :
# 1. Un repere proprement dit
repere = ("O", "I", "J") # en majuscule, ce sont des points ; en minuscule, des vecteurs.
# 2. Deux axes gradues
origine_axes = (0, 0)
# Pour choisir le mode :
utiliser_repere = True
# -> utiliser ou non un rep�re (m�me origine sur chaque axe...)
# -> si on n'utilise pas le rep�re, on affiche deux valeurs distinctes � l'intersection des axes

gradu = (1, 1) # espacement entre deux graduations pour chaque axe. (0 => pas de graduations).
saturation =  0.3 # valeur de saturation pour le coefficient pas()/gradu
# au dela du coefficient de saturation, les graduations ne sont plus affichees
# cela evite de bloquer le programme...

# Nombre de cm pour une unit� en export
echelle_cm = (1, 1)

# Couleur de fond des figures.
couleur_fond = "w"

afficher_quadrillage = True # affiche un quadrillage a la place des graduations
quadrillages = (((None, None), ":", .5, "k"),)
# Chaque couple correspond a un quadrillage.
# Le format est : ([espacement horizontal, espacement vertical], style, epaisseur, couleur).
# On peut omettre des elements :
# quadrillages = ((),)
# Si un espacement vaut None, la valeur de gradu correspondante sera utilisee.
# Valeurs possibles pour le style : (cf http://matplotlib.sourceforge.net/matplotlib.pylab.html#-plot)
# "--" tirets
# "-" lignes continues
# ":" points
# "-." alternance de points et de tirets
# On peut superposer plusieurs quadrillages :
# quadrillages = (((1, 1), "-", 0.25, "k"), ((0.25, 0.25), ":", .25, "k"),)
# ou encore :
# quadrillages = (((1, 1), ":", 1, "k"), ((0.2, 0.2), ":", .125, "k"),)
couleur_papier_millimetre = '#aa7733' # couleur � utiliser pour le papier millim�tr� entre autres

resolution = 1000 # resolution utilisee pour le tracage des courbes (plus la valeur est importante, plus la courbe est lisse)
fenetre = (origine_axes[0]-8, origine_axes[0]+8, origine_axes[1]-5, origine_axes[1]+5)   # xmin, xmax, ymin, ymax

zoom_in = 1.1 # coefficient d'agrandissement des objets lors d'un zoom.
zoom_out = 0.9 # coefficient de reduction des objets lors d'un zoom.

zoom_texte_in = 1.05
zoom_texte_out = 0.95

zoom_ligne_in = 1.07
zoom_ligne_out = 0.93

dpi_ecran = 80
# Tableau r�capitulatif des r�solutions les plus courantes :
# http://forum.notebookreview.com/notebook-dummy-guide-articles/124093-guide-screen-sizes-dots-per-inch-dpi.html

dpi_export = 200 # resolution utilisee lors de l'exportation des images
compresser_geo = False # compresser les fichiers .geo par d�faut

afficher_coordonnees = True # affiche en permanence les coordonnees
afficher_pixels = False # pour d�bogage (mettre afficher_coordonnes � False pr�c�demment)

afficher_objets_caches = False # affiche en gris� les objets masqu�s

precision_selection = 10 # plus la precision est importante, plus il faut etre pres d'un objet pour pouvoir le saisir
# Si le chiffre est trop petit, ca devient fastidieux de selectionner un objet
# A l'inverse, s'il est trop grand, il devient difficile de selectionner celui qu'on veut entre deux objets proches


nom_multiple = False # autorise � 'nommer' plusieurs objets avec le m�me nom
# (en fait, un seul objet aura le nom 'A' par exemple, les autres auront 'A' comme �tiquette).

# ------------------------------
# Code � r��crire
# Tranformation lin�aire appliqu�e au graphique : (EXPERIMENTAL !)
transformation = None
# Couple de la forme (a, b, c, d) tel que :
# |x'|     |a b| |x|
# |y'|  =  |c d| |y|
# Exemple (permutation des axes) :
#transformation = (0, 1, 1, 1)
# ------------------------------

afficher_barre_outils = False
afficher_console_geolib = False

# Tenter la virgule comme s�parateur si le point a �chou�, et vice-versa.
# (� d�sactiver pour faciliter le d�bogage.)
adapter_separateur = True



# R�pertoires par d�faut
# ----------------------

# R�pertoire o� on sauve les fichiers par d�faut
rep_save = None
# rep_save = repertoire
# R�pertoire o� on ouvre les fichiers par d�faut
rep_open = None
# rep_open = repertoire
# R�pertoire o� on exporte les fichiers par d�faut
rep_export = None
# rep_export = repertoire


emplacements = {}

taille_max_log = 10000 # taille max du fichier de log (en Ko)

taille_max_log *= 1024


try:
    from .personnaliser import * # permet de g�n�rer un fichier personnaliser.py lors de l'installation, ou de la premi�re utilisation, et dont les parametres remplaceront ceux-ci.
except ImportError:
    try:
        from .personnaliser_ import *
    except ImportError:
        pass

if install:
    # Les pr�f�rences, fichiers log, etc... sont stock�s dans le dossier de l'utilisateur.
    # ~ se r�f�re au r�pertoire de l'utilisateur (ex: /home/BillG/ sous Linux, ou C:\Documents and Settings\LTorvald\ sous Windows)
    emplacements.setdefault("log", "~/.wxgeometrie/log")
    emplacements.setdefault("preferences", "~/.wxgeometrie/preferences")
    emplacements.setdefault("macros", "~/.wxgeometrie/macros")
    emplacements.setdefault("session", "~/.wxgeometrie/session")
else:
    # Utilisation sans installation. Tout est stock� directement dans le dossier wxgeometrie/.
    # % se r�f�re au dossier contenant WxGeometrie (indiqu� par param.EMPLACEMENT)
    emplacements.setdefault("log", "%/log") # dans log/ par d�faut
    emplacements.setdefault("preferences", "%/preferences") # dans preferences/ par d�faut
    emplacements.setdefault("macros", "%/macros") # dans macros/ par d�faut
    emplacements.setdefault("session", "%/session") # dans session/ par d�faut

print(u'Import des param�tres termin�.')
