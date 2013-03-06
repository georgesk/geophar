# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Objets                    #
##--------------------------------------#######
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

import re
from cmath import exp as cexp, log as clog
from math import pi

from .objet import Ref, Argument, Arguments, ArgumentNonModifiable, Objet, \
                   RE_NOM_OBJET, FILL_STYLES
from .points import Point_generique, Point, Barycentre, Point_pondere
from .lignes import Segment
from .routines import point_dans_enveloppe_convexe, segments_secants, point_dans_polygone
from .transformations import Translation, Rotation
from .vecteurs import Vecteur
from ..pylib import is_in, print_error
from .. import param


##########################################################################################

# Perspectives cavali�res








class Arete(Segment):
    u"""Une ar�te.

    Une ar�te d'un poly�dre, reliant le point numero 'n' au point numero 'p'.
    Note: n et p commencent � 0.
    L'objet est cr�� automatiquement lors de la cr�ation du poly�dre.
    De plus, si l'objet est supprim�, le poly�dre est automatiquement supprim�."""

    _prefixe_nom = "a"

    polyedre = __polyedre = ArgumentNonModifiable("Polyedre_generique")
    n = __n = ArgumentNonModifiable("int")
    p = __p = ArgumentNonModifiable("int")

    def __new__(cls, polyedre, n, p, **styles):
        try:
            return polyedre.aretes[n]
            # Attention, Arete.__init__() va �tre appel� de nouveau !
        except (AttributeError, IndexError):
            arete = object.__new__(cls)
            return arete

    def __init__(self, polyedre, n, p, **styles):
        if not self._initialise:
            self.__polyedre = polyedre
            self.__n = n
            self.__p = p
            self._cachee = False
            Segment.__init__(self, polyedre._Polyedre_generique__sommets[n], polyedre._Polyedre_generique__sommets[p], **styles)
            self.__polyedre._cache.remove('test_aretes')
        else:
            self.style(**styles)

    def supprimer(self):
        self.__polyedre.supprimer()

    def _modifier_hierarchie(self, valeur = None):
        # Voir commentaires pour Sommet_polyedre._modifier_hierarchie
        N = len(self.__polyedre._Polyedre_generique__points)
        Objet._modifier_hierarchie(self, self.__polyedre._hierarchie + (self.__n + self.__p/N + N + 2)/(3*N + 2))

    def cachee(self, value = None):
        if value is True:
            self._cachee = True
            self.style(style = "--")
        elif value is False:
            self._cachee = False
            self.style(style = "-")
        return self._cachee

    cachee = property(cachee, cachee)

    def _creer_figure(self):
        # On s'assure que le test des ar�tes a bien eu lieu.
        self.__polyedre._cache.get('test_aretes', self.__polyedre._tester_aretes)
        Segment._creer_figure(self)



class Sommet_polyedre(Point_generique):
    u"""Un sommet.

    Le ni�me sommet d'un poly�dre.
    Note: n commence � 0.
    L'objet est cr�� automatiquement lors de la cr�ation du polyedre.
    De plus, si l'objet est supprim�, le poly�dre est automatiquement supprim�."""

    _prefixe_nom = "S"

    # Un sommet peut-�tre li� � un point, c'est-�-dire avoir toujours les m�mes coordonn�es que ce point
    _point_lie = None

    polyedre = __polyedre = ArgumentNonModifiable("Polyedre_generique")
    n = __n = ArgumentNonModifiable("int")

    def __new__(cls, polyedre, n, **styles):
        try:
            # Si le sommet existe d�j�, on retourne simplement le sommet existant.
            # Ceci �vite de cr�er en double le m�me sommet, lorsque la feuille
            # est sauvegard�e puis recharg�e. En effet, lors du chargement de la
            # feuille, des sommets vont �tre cr��s automatiquement � la cr�ation
            # du polygone, puis de nouveau lorsque `S0 = Sommet(p, 0, ...)` va
            # �tre ex�cut�.
            return polyedre.sommets[n]
            # Attention, Sommet.__init__() va �tre appel� de nouveau !
        except (AttributeError, IndexError):
            sommet = object.__new__(cls)
            return sommet

    def __init__(self, polyedre, n, **styles):
        if not self._initialise:
            self.__polyedre = polyedre
            self.__n = n
            Point_generique.__init__(self, **styles)
        else:
            self.style(**styles)

    def _get_coordonnees(self):
        return self.__polyedre._Polyedre_generique__points[self.__n].coordonnees

    def _set_coordonnees(self, x, y):
        if self._point_lie is not None:
            self._point_lie._set_coordonnees(x, y)

    def _modifier_hierarchie(self, valeur = None):
        # Pour les sauvegardes par exemple, il est pr�f�rable que les sommets, puis les ar�tes,
        # apparaissent juste apr�s la construction du poly�dre ; ils doivent occuper des places cons�cutives dans la hi�rarchie.
        # Par exemple, si le poly�dre a 4 sommets, et si sa place dans la hi�rarchie est 18, ses trois sommets
        # auront  comme valeur hi�rarchique, dans l'ordre, 18.1, 18.2, 18.3 et 18.4,
        # et ses ar�tes auront pour valeur hi�rarchique 18.6, 18.7, 18.8, 18.9.
        N = len(self.__polyedre._Polyedre_generique__points)
        Objet._modifier_hierarchie(self, self.__polyedre._hierarchie + (self.__n + 1)/(3*N + 2))

    def _lier_sommet(self, point):
        u"""Lie le sommet � un point, en le rendant d�pla�able."""
        self._point_lie = point
        self.style(couleur = "m")

    def _deplacable(self, *args, **kw):
        return self._point_lie is not None

    _deplacable = _modifiable = property(_deplacable, _deplacable)





class Polyedre_generique(Objet):
    u"""Un poly�dre g�n�rique.

    Classe m�re de toutes les repr�sentations de poly�dres."""

    _style_defaut = param.polyedres
    _prefixe_nom = "p"

    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        n = len(points)
        self.__points = points = tuple(Ref(obj) for obj in points)
        self.__centre = Barycentre(*(Point_pondere(point, 1) for point in points))
        Objet.__init__(self, **styles)
#        self.etiquette = Label_polyedre(self)
        self.__sommets = tuple(Sommet_polyedre(self, i) for i in xrange(n))
        # 'aretes' contient la liste des ar�tes sous la forme de couples de num�ros de sommets.
        # ex: [(0, 1), (0, 2), (0,3), (1, 2), (1, 3), (2, 3)] pour un t�tra�dre.
        aretes = styles.pop("aretes", [])
        self.__aretes = tuple(Arete(self, i, j) for i, j in aretes)
        # 'faces' contient la liste des faces sous la forme de tuples de num�ros de sommets.
        # ex: [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)] pour un t�tra�dre.
        faces = styles.pop("faces", [])
        self.__faces = tuple(faces)
        # Les faces 'principales' seront colori�es plus fonc�es.
        # Typiquement, il s'agit de la vue de face.
        faces_principales = styles.pop("faces_principales", [])
        self.__faces_principales = tuple(faces_principales)


    def on_register(self):
        u"""Enregistre les ar�tes et les sommets du polyedre dans la feuille lors
        de l'enregistrement du polyedre."""
        # On enregistre toutes les ar�tes dans la feuille.
        for arete in self.__aretes:
            self.feuille.objets.add(arete)

        # on enregistre ensuite les sommets.
        # On essaie de nommer intelligemment les sommets.
        # Par exemple, si un rectangle s'appelle ABCD, les points libres
        # s'appelleront si possible A et B, et les deux autres sommets
        # s'appelleront C et D.
        sommets = []
        noms_args, args = zip(*self._iter_arguments)
        for sommet, point in zip(self.__sommets, self.__points):
            sommets.append(point if is_in(point, args) else sommet)

        n = len(sommets)

        noms = re.findall(RE_NOM_OBJET, self._nom)
        if ''.join(noms) == self._nom and len(noms) == n:
            for sommet, nom in zip(sommets, noms):
                if sommet._nom and sommet._nom != nom:
                    noms = n*['']
                    break
        else:
            noms = n*['']

        add = self.feuille.objets.add
        for sommet, nom in zip(sommets, noms):
            if not sommet._nom:
                add(sommet, nom_suggere=nom)

        if self._valeurs_par_defaut:
            # Par d�faut, on essaie d'�viter un polygone crois�, � l'aide
            # de la m�thode `._affecter_coordonnees_par_defaut()`.
            if len(args) == n:
                if all(isinstance(arg, Point) for arg in args):
                    self._affecter_coordonnees_par_defaut(args)
            self._valeurs_par_defaut = []


    @property
    def centre(self):
        return self.__centre

    centre_gravite = centre

    @property
    def sommets(self):
        return self.__sommets

    @property
    def aretes(self):
        return self.__aretes

##    @property
##    def faces(self):
##        return self.__faces


    def _creer_figure(self):
        if not self._representation:
            self._representation = [self.rendu.polygone() for face in self.__faces]

        for face, fill in zip(self.__faces,  self._representation):
            xy = [self.__points[n].coordonnees for n in face + (face[0],)]
            niveau = self.style("niveau")
            couleur = self.style("couleur")
            fill.xy = xy
            if face in self.__faces_principales:
                fill.set_alpha(min(2*self.style("alpha"), 1.))
            else:
                fill.set_alpha(self.style("alpha"))
            hachures = self.style("hachures")
            if hachures is not None:
                fill.set_hatch(hachures)
            fill.set(edgecolor=couleur, facecolor=couleur)
            fill.zorder = niveau - 0.01
            fill.set_linestyle(FILL_STYLES.get(self.style("style"), "solid"))


##    def image_par(self, transformation):
##        return Polyedre(*(point.image_par(transformation) for point in objet._Polyedre_generique__points))

    def _distance_inf(self, x, y, d):
        xy = [self._pixel(pt) for pt in self.__points]
        return point_dans_enveloppe_convexe((x,y), xy)



    def _espace_vital(self):
        points = self.__points
        x1 = min(pt.abscisse for pt in points)
        x2 = max(pt.abscisse for pt in points)
        y1 = min(pt.ordonnee for pt in points)
        y2 = max(pt.ordonnee for pt in points)
        return (x1, x2, y1, y2)

    def _secantes(self, arete1, arete2):
        p1, p2 = arete1
        p3, p4 = arete2
        return segments_secants(self.__points[p1], self.__points[p2], self.__points[p3], self.__points[p4])


    def _tester_aretes(self):
        u"M�thode � surclasser."
        raise NotImplementedError




class Tetraedre(Polyedre_generique):
    u"""Un t�tra�dre.

    La projection d'un t�tra�dre."""

    point1 = __point1 = Argument("Point_generique", defaut = lambda:Point())
    point2 = __point2 = Argument("Point_generique", defaut = lambda:Point())
    point3 = __point3 = Argument("Point_generique", defaut = lambda:Point())
    point4 = __point4 = Argument("Point_generique", defaut = lambda:Point())

    def __init__(self, point1 = None, point2 = None, point3 = None, point4 = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__point3 = point3 = Ref(point3)
        self.__point4 = point4 = Ref(point4)
        styles["aretes"] = [(0, 1), (0, 2), (1, 2), (0,3), (1, 3), (2, 3)]
        styles["faces"] = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        styles["faces_principales"] = [(0, 1, 2)]
        Polyedre_generique.__init__(self, point1, point2, point3, point4, **styles)



    def _tester_aretes(self):
        print "Test aretes 1", self.__point1.coordonnees
        print "Test aretes 2", self.__point2.coordonnees
        print "Test aretes 3", self.__point3.coordonnees
        print "Test aretes 4", self.__point4.coordonnees
        # Ce qui suit doit �tre g�r� *avant* l'affichage du poly�dre, et de ses ar�tes.
        if point_dans_polygone(self.__point4.coordonnees,
                [self.__point1.coordonnees, self.__point2.coordonnees, self.__point3.coordonnees]):
            print "3 cachees -> ok"
            self._Polyedre_generique__aretes[3].cachee = True
            self._Polyedre_generique__aretes[4].cachee = True
            self._Polyedre_generique__aretes[5].cachee = True
        else:
            self._Polyedre_generique__aretes[3].cachee = self._secantes((1, 2), (0, 3))
            self._Polyedre_generique__aretes[4].cachee = self._secantes((0, 2), (1, 3))
            self._Polyedre_generique__aretes[5].cachee = self._secantes((0, 1), (2, 3))







class Sommet_cube(Point_generique):
    u"""Un sommet d'un rectangle.

    (Usage interne)."""

    _style_defaut = param.points_deplacables

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    angle = __angle = Argument("Angle_generique", defaut = pi/6)
    rapport = __rapport = Argument("Variable_generique", defaut = 0.6)

    def __init__(self, point1, point2, angle, rapport, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        self.__rapport = rapport = Ref(rapport)
        Point_generique.__init__(self, **styles)

    def _get_coordonnees(self):
        k = self.__rapport
        a = self.__angle.radian
        zA = self.__point1.z
        zB = self.__point2.z
        zE = k*cexp(1j*a)*(zB - zA) + zA
        print "HHeLiBeBCNOFNe", k*cexp(1j*a), (zB - zA), zA, zE
        return zE.real, zE.imag

    def _set_coordonnees(self, x, y):
        zA = self.__point1.z
        zB = self.__point2.z
        z = x + 1j*y
        try:
            if abs(zB - zA) > param.tolerance:
           # TODO: cas o� l'angle n'est pas en radian
                self.__angle.val = clog((z - zA)/(zB - zA)).imag
        except (OverflowError, ZeroDivisionError):
            if param.debug:
                print_error()



class Cube(Polyedre_generique):
    u"""Un cube.

    La projection d'un cube."""

    point1 = __point1 = Argument("Point_generique", defaut = Point)
    point2 = __point2 = Argument("Point_generique", defaut = Point)
    angle = __angle = Argument("Angle_generique", defaut = pi/6)
    rapport = __rapport = Argument("Variable_generique", defaut = 0.6)


    def _tester_aretes(self):
        # Ce qui suit doit �tre g�r� *avant* l'affichage du poly�dre, et de ses ar�tes.
        pts = self._Polyedre_generique__points
        aretes = self._Polyedre_generique__aretes
        face_avant = pts[:4]
        # cas o� un des sommets est cach� par la face avant
        for i in (4, 5, 6, 7):
            if point_dans_polygone(pts[i], face_avant):
                for arete in aretes:
                    if arete._Arete__n == i or arete._Arete__p == i:
                        arete.cachee = True
                    else:
                        arete.cachee = False
                return Polyedre_generique._conditions_existence(self)
        # sinon, on cherche quelle arr�te "coupe" la face avant.
        for i in (4, 5, 6, 7):
            j = i - 4 # sommet correspondant de la face avant
            if self._secantes((i, j), ((j + 1)%4, (j + 2)%4)) or self._secantes((i, j), ((j + 2)%4, (j + 3)%4)):
                for arete in aretes:
                    if arete._Arete__n == i or arete._Arete__p == i:
                        arete.cachee = True
                    else:
                        arete.cachee = False
        return Polyedre_generique._conditions_existence(self)


    def __init__(self, point1 = None, point2 = None, angle = None, rapport = None, **styles):
        self.__point1 = point1 = Ref(point1)
        self.__point2 = point2 = Ref(point2)
        self.__angle = angle = Ref(angle)
        self.__rapport = rapport = Ref(rapport)
        styles["aretes"] = [(0, 1), (1, 2), (2, 3), (3, 0), # face avant
                            (4, 5), (5, 6), (6, 7), (7, 4), # face arri�re
                            (0, 4), (1, 5), (2, 6), (3, 7)]
        styles["faces"] = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        styles["faces_principales"] = [(0, 1, 2, 3)]
        point3 = Rotation(point2, -pi/2)(point1)
        point4 = Rotation(point1, pi/2)(point2)
        point5 = Sommet_cube(point1, point2, angle, rapport)
        t = Translation(Vecteur(point1, point5))
        point6 = t(point2)
        point7 = t(point3)
        point8 = t(point4)
        Polyedre_generique.__init__(self, point1, point2, point3, point4, point5, point6, point7, point8, **styles)
        self._Polyedre_generique__sommets[4]._lier_sommet(point5)
