# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

##--------------------------------------#######
#                 Fenetres                              #
##--------------------------------------#######
#    WxGeometrie
#    Dynamic geometry, graph plotter, and more for french mathematic teachers.
#    Copyright (C) 2005-2013  Nicolas Pourcelot
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

from operator import attrgetter
from functools import partial

from PyQt4.QtGui import (QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                         QLineEdit, QPushButton, QMenu, QCursor)
from PyQt4.QtCore import Qt, QSize

from .qtlib import MultipleChoiceDialog
from ..pylib import regsub
from ..geolib.textes import Texte
from ..geolib.points import Point_generique, Barycentre, Point, Milieu, Centre,\
                            Orthocentre, Centre_cercle_circonscrit, Centre_cercle_inscrit,\
                            Glisseur_droite, Glisseur_cercle, Glisseur_segment,\
                            Centre_gravite, Point_final
from ..geolib.cercles import Cercle_generique, Cercle, Arc_points,\
                             Arc_oriente, Cercle_diametre, Cercle_rayon, Demicercle,\
                             Arc_cercle, Disque, Cercle_points
from ..geolib.lignes import Droite_generique, Segment, Demidroite, Ligne_generique,\
                            Droite, Tangente, Parallele, Perpendiculaire, Bissectrice,\
                            Mediatrice
from ..geolib.polygones import Polygone_regulier, Triangle, Polygone,\
                               Parallelogramme, Polygone_regulier_centre
from ..geolib.angles import Angle_generique, Angle, Angle_oriente,\
                            Angle_libre, Angle_vectoriel
from ..geolib.transformations import Rotation, Homothetie, Translation, Reflexion,\
                              Symetrie_centrale
from ..geolib.vecteurs import Vecteur_generique, Vecteur, Vecteur_libre, Representant
from ..geolib.intersections import Intersection_cercles, Intersection_droite_cercle,\
                            Intersection_droites
from ..geolib.interpolations import Interpolation_lineaire, Interpolation_quadratique
from ..geolib.variables import Variable
from ..geolib.objet import Objet
from .. import param


def repr_str(chaine):
    u'Force la chaîne a être représentée entourée de guillemets doubles (").'
    return repr(chaine + "'")[:-2] + '"'


####################################################################################################

# Differentes boites de dialogue pour creer des objets geometriques


class Dialogue(QDialog):

    objet = None # classe associee (utilise pour les boites de dialogue de creation d'objets geometriques)

    def __init__(self, parent, titre="", size=None):
        u"""S'il s'agit d'un dialogue pour la création d'objets,
        le titre par défaut est généré automatiquement à partir de l'attribut de classe 'objet'."""

        QDialog.__init__(self, parent)

        if self.objet and not titre:
            titre = u"Créer " + self.objet.titre()
        self.setWindowTitle(titre)

        if size is not None:
            self.setMinimumSize(*size)
         # Qt::WindowContextHelpButtonHint

        # En cas de changement d'onglet, cela permet de pointer toujours sur l'onglet initial
        self.onglet_actuel = parent.onglet_actuel
        self.sizer = QVBoxLayout()
        self.champs = {}

        if self.objet:
            self.ajoute([("Nom %s : " %self.objet.titre("du", False)), ("nom", 10)],
                        u"Entrez le nom de l'objet. Exemples : A, AB, Cercle, M2...")



    def ajoute(self, contenu, aide = ""):
        u"""Ajoute une ligne de contenu dans la boite de dialogue.

        Format du contenu : ("texte statique",("nom de champ", taille), etc...)
        Exemple : ("entrez l'abscisse :",("absc",10),"cm")
        Pour un champ, un 3e argument peut-être indiqué pour donner le type d'objet,
        s'il s'agit d'un objet géométrique (ou None).
        Un 4e argument peut-etre saisi, pour donner le comportement en cas d'agrandissement,
        et un 5e, pour indiquer une valeur initiale du champ.
        Le champ créé sera accessible via self.champ("abcs").

        L'argument type d'objet sert à faire des propositions à l'utilisateur lors d'un clic du milieu.

        Le type d'objet peut-être compris dans une liste d'un seul élement, par exemple : [Point_generique]
        Cela signifie alors que le champ doit contenir une liste de points, et non un seul point.

        A noter qu'un tuple, comme (Point_generique, Vecteur), par contre,
        correspond au comportement habituel de Python:
        l'objet est soit un Point_generique, soit un Vecteur
        """

        self.box = QHBoxLayout()
        for txt in contenu:
            if isinstance(txt, (str, unicode)):
                # texte statique
                texte = QLabel(txt)
                texte.setWhatsThis(aide)
                self.box.addWidget(texte)

            else:
                # champ de saisie
                ql = self.champs[txt[0]] = QLineEdit(self)
                ql.setText(str(txt[4]) if len(txt) >= 5 else "")
                ql.setMinimumWidth(10*txt[1])
                ql.setWhatsThis(aide)
                self.box.addWidget(ql)#, (len(txt) >= 4) and txt[3] or 0, wx.ALIGN_CENTRE|wx.ALL, 5)
                if len(txt) >= 3 and txt[2] is not None:
                    ql.setContextMenuPolicy(Qt.CustomContextMenu)
                    ql.customContextMenuRequested.connect(partial(self.right_click, type=txt[2], champ=ql))
                    # XXX: traduire en Qt

        self.sizer.addLayout(self.box)


    def finalise(self):     # cette fonction est a appeler une fois tout le contenu ajoute.
        line = QFrame(self)#, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        line.setFrameStyle(QFrame.HLine)
        self.sizer.addWidget(line)

        self.box = QHBoxLayout()

        ##if wx.Platform != "__WXMSW__":
            ##btn = wx.ContextHelpButton(self)
            ##self.box.Add(btn)

        btn = QPushButton(u" Créer " if self.objet else u"Enregistrer", clicked=self.accept)
        btn.setWhatsThis(u"Créer l'objet." if self.objet else u"Enregistrer les modifications.")
        ##btn.SetDefault()
        #XXX: Action à ajouter !!
        self.box.addWidget(btn)

        btn = QPushButton(u"Annuler", clicked=self.close)
        btn.setWhatsThis(u"Quitter sans rien changer.")
        self.box.addWidget(btn)

        self.sizer.addLayout(self.box)

        self.setLayout(self.sizer)
        if self.objet:
            self.champs['nom'].setFocus()

    def affiche(self):
        return self.exec_()

    def commande(self):
        return self.champ("nom") + "=" + self.objet.classe() + "(" + self.parametres() + ")"

    def champ(self, etiquette):
        return self.champs[etiquette].text()

    def parametres(self):   # le parametre par defaut est None
        return ",".join([etiquette + "=" + (self.champ(etiquette).strip() or "None")
                         for etiquette in self.champs if etiquette != "nom"])


    def right_click(self, type, champ):
        u"Retourne une fonction qui sera executée lors d'un clic droit sur le champ 'champ'."
        champ.setFocus()
        plusieurs = isinstance(type, list)
        if plusieurs:
            type = type[0]
        liste_objets = self.onglet_actuel.feuille_actuelle.objets.lister(False, type = type)
        liste_objets.sort(key = attrgetter('nom')) # ordre alphabétique
        if not liste_objets:
            return
        menu = QMenu()

        for obj in liste_objets:
            action = menu.addAction(obj.nom_complet)
            action.nom = obj.nom

        action = menu.exec_(QCursor.pos())
        if action:
            if plusieurs:
                # le champ doit contenir non pas un objet, mais une liste d'objets
                val = champ.text().strip()
                if val:
                    if not val.endswith(","):
                        val += ","
                    val += " "
                champ.setText(val + action.nom)
            else:
                # le champ contient un seul objet
                champ.setText(action.nom)



class DialoguePoint(Dialogue):
    objet = Point
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Coordonnées du point :"], u"Entrez les coordonnées de votre nouveau point.")
        self.ajoute([u"Abscisse :", ("x", 10, Variable)], u"Entrez ici l'abscisse du point. Exemple : 3.25")
        self.ajoute([u"Ordonnée :", ("y", 10, Variable)], u"Entrez ici l'ordonnée du point. Exemple : -5")
        self.finalise()



class DialogueSegment(Dialogue):
    objet = Segment
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Extrémités du segment :"], u"Entrez les extrémités du nouveau segment.")
        self.ajoute([u"Premier point :", ("point1", 10, Point_generique)], u"Entrez ici le premier point. Exemple : A")
        self.ajoute([u"Deuxième point :", ("point2", 10, Point_generique)], u"Entrez ici le deuxième point. Exemple : B")
        self.finalise()



class DialogueDroite(Dialogue):
    objet = Droite
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Donnez deux points de la droite :"], u"Définissez la droite en entrant deux points de la droite.")
        self.ajoute([u"Premier point :", ("point1", 10, Point_generique)], u"Entrez ici le premier point. Exemple : A")
        self.ajoute([u"Deuxième point :", ("point2", 10, Point_generique)], u"Entrez ici le deuxième point. Exemple : B")
        self.finalise()



class DialogueDemidroite(Dialogue):
    objet = Demidroite
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Donnez deux points de la demi-droite :"], u"Définissez la demi-droite en entrant son origine, et un autre point.")
        self.ajoute([u"Origine :", ("origine", 10, Point_generique)], u"Entrez ici son origine. Exemple : A")
        self.ajoute([u"Deuxième point :", ("point", 10, Point_generique)], u"Entrez ici un deuxième point. Exemple : B")
        self.finalise()


class DialogueVecteur(Dialogue):
    objet = Vecteur
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Extremités du vecteur :"], u"Entrez les extremités du nouveau vecteur.")
        self.ajoute([u"Point de départ :", ("point1", 10, Point_generique)], u"Entrez ici le premier point. Exemple : A")
        self.ajoute([u"Point d'arrivée :", ("point2", 10, Point_generique)], u"Entrez ici le deuxieme point. Exemple : B")
        self.finalise()


class DialogueVecteurLibre(Dialogue):
    objet = Vecteur_libre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Coordonnées du vecteur :"], u"Entrez les coordonnées de votre nouveau vecteur.")
        self.ajoute([u"Abscisse :", ("x", 10, Variable)], u"Entrez ici l'abscisse du vecteur. Exemple : 3.25")
        self.ajoute([u"Ordonnée :", ("y", 10, Variable)], u"Entrez ici l'ordonnée du vecteur. Exemple : -5")
        self.finalise()


class DialogueRepresentant(Dialogue):
    objet = Representant
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un représentant du vecteur :", ("vecteur", 10, Vecteur_generique)], u"Entrez ici un nom de vecteur. Exemple : u")
        self.ajoute([u"ayant pour origine le point :", ("origine", 10, Point_generique)], u"Entrez ici le point origine du vecteur. Exemple : A")
        self.finalise()


class DialogueMilieu(Dialogue):
    objet = Milieu
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Construire le milieu des points :"], u"Entrez les extrémités du segment.")
        self.ajoute([u"Premier point :", ("point1", 10, Point_generique)], u"Entrez ici le premier point. Exemple : A")
        self.ajoute([u"Deuxième point :", ("point2", 10, Point_generique)], u"Entrez ici le deuxième point. Exemple : B")
        self.finalise()



class DialogueBarycentre(Dialogue):
    objet = Barycentre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Construire le barycentre :"], u"Entrez les points, puis les coefficients.")
        self.ajoute([u"des points :", ("points", 10)], u"Entrez ici les points séparés par des virgules. Exemple : A,B,C")
        self.ajoute([u"avec les coefficients :", ("coeffs", 10)], u"Entrez ici les coefficients (de somme non nulle !) séparés par des virgules. Exemple : 5,3,1.5")
        self.finalise()

    def parametres(self):
        return "*zip((" + self.champ("points") + "),(" + self.champ("coeffs") + "))"




class DialoguePointFinal(Dialogue):
    objet = Point_final
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Construire le point tel qu'on ait :"], u"Entrez la relation vectorielle.")
        self.ajoute([("point1", 2, Point_generique), ">", ("point2", 2, Point_generique), "=", ("relation", 10, Point_generique, 1)], \
        u"""Entrez ici la relation vectorielle. Exemple, si N est le point à construire :\nA>N = 2 B>C + 5/3 D>E.
        Attention : le membre de droite ne doit contenir que des points déjà existants.""")
        self.finalise()

    def commande(self):
        #~ relation = regexp("[A-Z_a-z][A-Z_a-z0-9 ]*>[ ]*[A-Z_a-z][A-Z_a-z0-9]*", self.champ("relation"), "'(' + x + ')'")
        relation = regsub("[A-Z_a-z][A-Z_a-z0-9 ]*>[ ]*[A-Z_a-z][A-Z_a-z0-9]*", self.champ("relation"), lambda x:'(' + x + ')')
        #~ relation = regexp("[0-9][ ]*[(]", relation, "x[:-1] + '*('")
        relation = regsub("[0-9][ ]*[(]", relation, lambda x:x[:-1] + '*(')
        autre_point = self.champ("point1")
        if autre_point == self.champ("nom"):
            relation = "-(%s)" %relation
            autre_point = self.champ("point2")
        return self.champ("nom") + "=" + autre_point + "+(" +  relation + ")"





class DialogueCercleRayon(Dialogue):
    objet = Cercle_rayon
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un cercle de centre :", ("centre", 5, Point_generique)], u"Entrez ici le centre du cercle. Exemple : M")
        self.ajoute([u"et de rayon :", ("rayon", 5, Variable)], u"Entrez ici le rayon. Exemple : 3")
        self.finalise()



class DialogueCercle(Dialogue):
    objet = Cercle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un cercle de centre :", ("centre", 5, Point_generique)], u"Entrez ici le centre du cercle. Exemple : O")
        self.ajoute([u"auquel appartient :", ("point", 5, Point_generique)], u"Entrez ici un point du cercle. Exemple : M")
        self.finalise()



class DialogueCercleDiametre(Dialogue):
    objet = Cercle_diametre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Donnez un diamètre du cercle :"])
        self.ajoute([u"Créer un cercle de diamètre : [", ("point1", 5, Point_generique), ("point2", 5, Point_generique), "]"], u"Entrez les extrémités du diamètre. Exemple : A et B")
        self.finalise()


class DialogueCerclePoints(Dialogue):
    objet = Cercle_points
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Premier point du cercle :", ("point1", 5, Point_generique)], u"Entrez ici un point du cercle. Exemple : A")
        self.ajoute([u"Deuxième point : ", ("point2", 5, Point_generique)], u"Entrez un 2e point du cercle. Exemple : B")
        self.ajoute([u"Troisième point : ", ("point3", 5, Point_generique)], u"Entrez ici un 3e point du cercle. Exemple : C")
        self.finalise()


class DialogueArcCercle(Dialogue):
    objet = Arc_cercle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Centre du cercle :", ("centre", 5, Point_generique)], u"Entrez ici le centre du cercle. Exemple : O")
        self.ajoute([u"Premier point de l'arc : ", ("point1", 5, Point_generique)], u"Entrez le 1er point de l'arc. L'arc est parcouru dans le sens direct. Exemple A")
        self.ajoute([u"Deuxième point : ", ("point2", 5, Point_generique)], u"Entrez un 2e point. Il ne sera pas forcément sur l'arc. Exemple : B")
        self.finalise()


class DialogueArcPoints(Dialogue):
    objet = Arc_points
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Premier point de l'arc :", ("point1", 5, Point_generique)], u"Entrez ici une extrémité de l'arc. Exemple : A")
        self.ajoute([u"Deuxième point : ", ("point2", 5, Point_generique)], u"Entrez un point de l'arc, distinct des extrémités. Exemple : B")
        self.ajoute([u"Troisième point : ", ("point3", 5, Point_generique)], u"Entrez ici l'autre extrémité de l'arc. Exemple : C")
        self.finalise()



class DialogueArcOriente(Dialogue):
    objet = Arc_oriente
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Premier point de l'arc :", ("point1", 5, Point_generique)], u"Entrez ici l'origine l'arc orienté. Exemple : A")
        self.ajoute([u"Deuxième point : ", ("point2", 5, Point_generique)], u"Entrez un point de l'arc, distinct des extrémités. Exemple : B")
        self.ajoute([u"Troisième point : ", ("point3", 5, Point_generique)], u"Entrez ici le point final de l'arc orienté. Exemple : C")
        self.finalise()



class DialogueDemiCercle(Dialogue):
    objet = Demicercle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Donnez un diametre du demi-cercle :"])
        self.ajoute([u"Créer une demi-cercle de diametre : [", ("point1", 5, Point_generique), ("point2", 5, Point_generique), "]"], u"Entrez les extremités du diamètre, dans le sens direct. Exemple : A et B")
        self.finalise()


class DialogueDisque(Dialogue):
    objet = Disque
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Donnez le cercle :"])
        self.ajoute([u"Créer un disque de circonférence :", ("cercle", 5, Cercle_generique)], u"Entrez le cercle délimitant le disque. Exemple : C")
        self.finalise()



class DialogueParallele(Dialogue):
    objet = Parallele
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la parallèle a :", ("droite", 5, Ligne_generique)], u"Entrez une droite. Exemple : d")
        self.ajoute([u"Passant par :", ("point", 5, Point_generique)], u"Entrez un point. Exemple : M")
        self.finalise()




class DialoguePerpendiculaire(Dialogue):
    objet = Perpendiculaire
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la perpendiculaire a :", ("droite", 5, Ligne_generique)], u"Entrez une droite. Exemple : d")
        self.ajoute([u"Passant par :", ("point", 5, Point_generique)], u"Entrez un point. Exemple : M")
        self.finalise()



class DialogueMediatrice(Dialogue):
    objet = Mediatrice
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la médiatrice du segment : [", ("point1", 5, Point_generique), ("point2", 5, Point_generique), "]"], u"Entrez les extremites du segment. Exemple : A et B")
        self.finalise()



class DialogueBissectrice(Dialogue):
    objet = Bissectrice
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la bissectrice de l'angle :", ("point1", 5, Point_generique), ("point2", 5, Point_generique), ("point3", 5, Point_generique)], u"Entrez le nom de l'angle, nommé par 3 points. Exemple : B A C")
        self.finalise()


class DialogueTangente(Dialogue):
    objet = Tangente
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la tangente au cercle :", ("cercle", 5, Cercle_generique)], u"Entrez le nom du cercle. Exemple : Cer")
        self.ajoute([u"Passant par :", ("point", 5)], u"Entrez un point. Exemple : M")
        self.finalise()


class DialogueInterDroites(Dialogue):
    objet = Intersection_droites
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer le point d'intersection des droites :", ("droite1", 5, Ligne_generique), "et", ("droite2", 5, Ligne_generique)], u"Entrez les noms des deux droites. Exemple : d1 et d2 ou (A B) et (C D)")
        self.finalise()


class DialogueInterDroiteCercle(Dialogue):
    objet = Intersection_droite_cercle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un point d'intersection entre :", u"la droite", ("droite", 5, Ligne_generique), u"et le cercle", ("cercle", 5, Cercle_generique)], u"Entrez les noms dela droite, et du cercle. Exemple : AB et Cer")
        self.finalise()


class DialogueInterCercles(Dialogue):
    objet = Intersection_cercles
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un point d'intersection des cercles :", ("cercle1", 5, Cercle_generique), "et", ("cercle2", 5, Cercle_generique)], u"Entrez les noms des deux cercles. Exemple : C1 et C2")
        self.finalise()




class DialogueGlisseurDroite(Dialogue):
    objet = Glisseur_droite
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un point sur la droite :", ("droite", 5, Droite_generique)], u"Entrez le nom de la droite. Exemple : d ou (A B)")
        self.finalise()




class DialogueGlisseurCercle(Dialogue):
    objet = Glisseur_cercle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un point sur le cercle :", ("cercle", 5, Cercle_generique)], u"Entrez le nom du cercle. Exemple : Cer")
        self.finalise()




class DialogueGlisseurSegment(Dialogue):
    objet = Glisseur_segment
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un point sur le segment :", ("segment", 5, Segment)], u"Entrez le nom du segment. Exemple : s ou [A B]")
        self.finalise()


class DialoguePolygone(Dialogue):
    objet = Polygone
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un polygone de sommets :", ("points", 10, [Point_generique])], u"Entrez les sommets du polygone. Exemple : A,B,C,D")
        self.finalise()

    def commande(self): # a cause de l'initialisation speciale de Polygone : __init__(*points)
        return self.champ("nom") + "=Polygone(" + self.champ("points") + ")"

class DialoguePolygoneRegulier(Dialogue):
    objet = Polygone_regulier
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un polygone régulier à", ("n", 5), u"sommets."], u"Entrez le nombre de sommets du polygone. Exemple : 7")
        self.ajoute([u"Premiers sommets", ("point1", 5, Point_generique), "et", ("point2", 5, Point_generique), u"(sens direct)."], u"Entrez le nom de deux sommets consécutifs. Exemple : A et B")
        self.finalise()


class DialoguePolygoneRegulierCentre(Dialogue):
    objet = Polygone_regulier_centre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un polygone régulier à", ("n", 5), u"sommets."], u"Entrez le nombre de sommets du polygone. Exemple : 7")
        self.ajoute([u"Passant par le sommet", ("sommet", 5, Point_generique), "et de centre", ("centre", 5, Point_generique)], u"Entrez le nom d'un sommet et du centre. Exemple : A et I")
        self.finalise()


class DialogueParallelogramme(Dialogue):
    objet = Parallelogramme
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un parallélogramme de trois premiers sommets :", ("point1", 5, Point_generique), ",", ("point2", 5, Point_generique), "et", ("point3", 5, Point_generique)], u"Entrez les 3 premiers sommets du parallélogramme (sens direct). Exemple : A,B et C")
        self.finalise()

class DialogueTriangle(Dialogue):
    objet = Triangle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer un triangle de sommets :", ("point1", 5, Point_generique), ",", ("point2", 5, Point_generique), "et", ("point3", 5, Point_generique)], u"Entrez le nom des points. Exemple : A , B et C")
        self.finalise()


class DialogueCentre(Dialogue):
    objet = Centre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer le centre du cercle :", ("cercle", 5, Cercle_generique)], u"Entrez le nom du cercle. Exemple : Cer")
        self.finalise()


class DialogueOrthocentre(Dialogue):
    objet = Orthocentre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer l'orthocentre du triangle :", ("triangle", 5, Triangle)], u"Entrez le nom du triangle. Exemple : ABC")
        self.finalise()


class DialogueCentreGravite(Dialogue):
    objet = Centre_gravite
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer le centre de gravité du polygone :", ("polygone", 5, Polygone)], u"Entrez le nom du polygone. Exemple : ABC")
        self.finalise()


class DialogueCentreCercleCirconscrit(Dialogue):
    objet = Centre_cercle_circonscrit
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer le centre du cercle circonscrit à :", ("triangle", 5, Triangle)], u"Entrez le nom du triangle. Exemple : ABC")
        self.finalise()


class DialogueCentreCercleInscrit(Dialogue):
    objet = Centre_cercle_inscrit
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer le centre du cercle inscrit dans :", ("triangle", 5, Triangle)], u"Entrez le nom du triangle. Exemple : ABC")
        self.finalise()

class DialogueAngle(Dialogue):
    objet = Angle
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer l'angle :", ("point1", 5, Point_generique), ("point2", 5, Point_generique), ("point3", 5, Point_generique)], u"Entrez les trois sommets de l'angle. Exemple : A B C")
        self.finalise()

class DialogueAngleOriente(Dialogue):
    objet = Angle_oriente
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer l'angle :", ("point1", 5, Point_generique), ("point2", 5, Point_generique), ("point3", 5, Point_generique)], u"Entrez les trois sommets de l'angle. Exemple : A B C")
        self.finalise()

class DialogueAngleLibre(Dialogue):
    objet = Angle_libre
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Valeur de l'angle :", ("valeur", 5)], u"Entrez la valeur en degré ou en radian de l'angle. Exemple : pi/2, 15°")
        self.ajoute([u"Unité (facultatif) :", ("unite", 5)], u"Entrez éventuellement l'unité. Exemple : r, d, g (degré, radian ou grad). Radian par défaut.")
        self.finalise()

    def commande(self): # gestion du symbole "°"
        valeur = self.champ("valeur").strip()
        if valeur.endswith(u"°"):
            valeur = valeur[:-1]
            unite = "'d'"
        else:
            unite = repr(self.champ("unite").lower().strip())
        return u"%s=Angle_libre(%s, %s)" %(self.champ("nom"), valeur, unite)


class DialogueAngleVectoriel(Dialogue):
    objet = Angle_vectoriel
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer l'angle : (", ("vecteur1", 5, Vecteur_generique), ",", ("vecteur2", 5, Vecteur_generique), ")"], u"Entrez les 2 vecteurs. Exemple : u et v, ou A>B et C>D")
        self.finalise()


class DialogueTexte(Dialogue):
    objet = Texte
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Texte :", ("texte", 10)], u"Entrez ici le texte. Exemple : Bonjour!")
        self.ajoute([u"Coordonnées du texte :"], u"Entrez les coordonnées de votre nouveau texte.")
        self.ajoute([u"Abscisse :", ("x", 10)], u"Entrez ici l'abscisse du texte. Exemple : 3.25")
        self.ajoute([u"Ordonnee :", ("y", 10)], u"Entrez ici l'ordonnée du texte. Exemple : -5")
        self.finalise()

    def commande(self): # Le champ texte doit etre converti...
        return "%s=Texte(%s,%s,%s)" %(self.champ("nom"), repr_str(self.champ("texte")), (self.champ("x") or "None"), (self.champ("y") or "None"))


class DialogueRotation(Dialogue):
    objet = Rotation
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la rotation d'angle ", ("angle", 5, Angle_generique), " et de centre ", ("centre", 5, Point_generique)], u"Entrez l'angle. Exemple : a, 60°, pi/2. Puis le centre. Exemple : A")
        self.ajoute([u"Unité :", ("unite", 5)], u"Entrez éventuellement l'unité. Exemple : r, d, g (degré, radian ou grad). Radian par défaut.")
        self.finalise()

    def commande(self): # gestion du symbole "°"
        angle = self.champ("angle").strip()
        if angle.endswith(u"°"):
            angle = angle[:-1]
            unite = "'d'"
        else:
            unite = self.champ("unite")
        return u"%s=Rotation(%s, %s, %s)" %(self.champ("nom"), self.champ("centre"), angle, unite)

class DialogueSymetrieCentrale(Dialogue):
    objet = Symetrie_centrale
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la symétrie de centre : ", ("centre", 5, Point_generique)],
                    u"Entrez un point. Exemple : A")
        #self.ajoute([u"Unité :", ("unite", 5)], u"Entrez éventuellement l'unité. Exemple : r, d, g (degré, radian ou grad). Radian par défaut.")
        self.finalise()


class DialogueTranslation(Dialogue):
    objet = Translation
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la translation de vecteur : ", ("vecteur", 5, Vecteur_generique)], u"Entrez un vecteur. Exemple : u, (1, 0), A>B")
        self.finalise()


class DialogueReflexion(Dialogue):
    objet = Reflexion
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la réflexion d'axe : ", ("droite", 5, Ligne_generique)], u"Entrez l'axe de la symétrie. Exemple : d, (A B)")
        self.finalise()


class DialogueHomothetie(Dialogue):
    objet = Homothetie
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer l'homothétie de centre : ", ("centre", 5, Point_generique),
                        u" et de rapport ", ("rapport", 5, Variable)],
                    u"Entrez un point (exemple: A) et un nombre (exemple: k, 3).")
        self.finalise()


class DialogueInterpolationLineaire(Dialogue):
    objet = Interpolation_lineaire
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Interpoler linéairement les points :", ("points", 20, [Point_generique])],
                    u"Entrez les points par lesquels la courbe doit passer. Exemple: A,B,C,D,E")
        self.ajoute([u"Extrémités comprises :", ("debut", 5), ("fin", 5)],
                    u"Indiquez si l'extrémité de début et de fin sont comprises. Exemple: o (ou oui), n (ou non)")
        self.finalise()

    def commande(self): # a cause de l'initialisation speciale de Polygone : __init__(*points)
        commande = self.champ("nom") + "=Interpolation_lineaire(" + self.champ("points")
        debut = self.champ("debut").lower()
        if debut in ("o", "oui", "y", "yes", "true"):
            commande += ", debut=True"
        elif debut in ("n", "non", "no", "false"):
            commande += ", debut=False"
        fin = self.champ("fin").lower()
        if fin in ("o", "oui", "y", "yes", "true"):
            commande += ", fin=True"
        elif fin in ("n", "non", "no", "false"):
            commande += ", fin=False"
        return commande + ")"


class DialogueInterpolationQuadratique(Dialogue):
    objet = Interpolation_quadratique
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Interpolation quadratique des points :", ("points", 20, [Point_generique])],
                    u"Entrez les points par lesquels la courbe doit passer. Exemple: A,B,C,D,E")
        self.ajoute([u"Extrémités comprises :", ("debut", 5), ("fin", 5)],
                    u"Indiquez si l'extrémité de début et de fin sont comprises. Exemple: o (ou oui), n (ou non)")
        self.finalise()

    def commande(self): # a cause de l'initialisation speciale de Polygone : __init__(*points)
        commande = self.champ("nom") + "=Interpolation_quadratique(" + self.champ("points")
        debut = self.champ("debut").lower()
        if debut in ("o", "oui", "y", "yes", "true"):
            commande += ", debut=True"
        elif debut in ("n", "non", "no", "false"):
            commande += ", debut=False"
        fin = self.champ("fin").lower()
        if fin in ("o", "oui", "y", "yes", "true"):
            commande += ", fin=True"
        elif fin in ("n", "non", "no", "false"):
            commande += ", fin=False"
        return commande + ")"


class DialogueVariable(Dialogue):
    objet = Variable
    def __init__(self, parent):
        Dialogue.__init__(self, parent)
        self.ajoute([u"Créer la variable de valeur : ", ("contenu", 15, Objet)],
                    u"Entrez une valeur, entre guillemets pour une valeur 'liée' (consultez l'aide). Exemple : 'A.x+1'")
        self.finalise()

class DialogueImage(Dialogue):
    def __init__(self, parent):
        Dialogue.__init__(self, parent, u"Créer l'image d'un objet par une transformation")
        self.ajoute([u"Nom de l'objet image : ", ("nom", 15, Objet)],
                    u"Entrez le nom de l'objet que vous voulez créer. Exemple : M, d.")
        self.ajoute([u"Objet de départ : ", ("objet", 15, Objet)],
                    u"Entrez le nom de l'antécédent. Exemple : A, d, [A B]")
        self.ajoute([u"Transformation : ", ("transformation", 15, Objet)],
                    u"Entrez la transformation (rotation, symétrie, etc...). Exemple : r, Rotation(O,pi/2)")
        self.finalise()

    def commande(self):
        return self.champ("nom") + "=" + self.champ("transformation") + "(" + self.champ("objet") + ")"

###############################################################################

class DialogueFenetre(Dialogue):
    def __init__(self, parent):
        Dialogue.__init__(self, parent, u"Régler la fenêtre d'affichage")
        fen = self.onglet_actuel.canvas.fenetre
        self.ajoute([u"Entrez les valeurs extrémales de la fenêtre d'affichage."])
        self.ajoute([u"Xmin :", ("xmin", 10, None, 1, round(fen[0], 4))], u"Abscisse minimale. Exemple : -5")
        self.ajoute([u"Xmax :", ("xmax", 10, None, 1, round(fen[1], 4))], u"Abscisse maximale. Exemple : 5")
        self.ajoute([u"Ymin :", ("ymin", 10, None, 1, round(fen[2], 4))], u"Ordonnée minimale. Exemple : -5")
        self.ajoute([u"Ymax :", ("ymax", 10, None, 1, round(fen[3], 4))], u"Ordonnée maximale. Exemple : 5")
        self.finalise()
        btn = QPushButton(u"Défaut", clicked=self.restaurer)
        btn.setWhatsThis(u"Restaurer le réglage par défaut de la fenêtre.")
        self.box.addWidget(btn)
        ##self.sizer.Fit(self)

    def commande(self):
        # Garder l'espace après la virgule (pour éviter la confusion avec le
        # séparateur décimal).
        return "fenetre = " + ', '.join(self.champs[nom].text()
                                   for nom in ('xmin', 'xmax', 'ymin', 'ymax'))

    def restaurer(self):
        self.champs["xmin"].setText(str(round(param.fenetre[0], 4)))
        self.champs["xmax"].setText(str(round(param.fenetre[1], 4)))
        self.champs["ymin"].setText(str(round(param.fenetre[2], 4)))
        self.champs["ymax"].setText(str(round(param.fenetre[3], 4)))


################################################################################



class SupprimerObjet(MultipleChoiceDialog):
    def __init__(self, parent):
        liste = parent.onglet_actuel.feuille_actuelle.inventaire()
        MultipleChoiceDialog.__init__(self, parent, u"Supprimer", u"Sélectionnez les objets à supprimer :", liste)
        ##self.resize(QSize(250, 400))


class EditerObjet(MultipleChoiceDialog):
    def __init__(self, parent):
        liste = parent.onglet_actuel.feuille_actuelle.inventaire()
        MultipleChoiceDialog.__init__(self, parent, u"Editer", u"Sélectionnez les objets à éditer :", liste)
        ##self.resize(QSize(250, 400))


