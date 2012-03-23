# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                   Interpolation                    #
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

# version unicode



from numpy import array, arange, append
# en test ###############
from numpy import poly1d
from scipy.interpolate import PiecewisePolynomial
import fractions as frac
#########################
from .objet import Ref, Argument, Arguments

from .courbes import Courbe_generique
from .lignes import Tangente_courbe
from .contexte import contexte

from ..pylib import fullrange
from .. import param

class Interpolation_generique(Courbe_generique):
    u"""Classe m�re de toutes les interpolations."""

    points = __points = Arguments("Point_generique")

    _style_defaut = param.interpolations

    def __init__(self, *points, **styles):
        self.__points = points = tuple(Ref(pt) for pt in points)
        Courbe_generique.__init__(self, **styles)


    def _affiche_extremites(self, vec_deb = None, vec_fin = None):
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        epaisseur = self.style("epaisseur")
        debut = self.style("debut")
        fin = self.style("fin")

        # D�but de la courbe
        plot = self._representation[-2]
        x, y = self.__points[0].coordonnees
        a, b = self.__points[1].coordonnees
        if vec_deb is None:
            vec_deb = (a - x, b - y)
        if debut is True:
            plot.set_data((x,), (y,))
            plot.set(visible=True, color=couleur, marker="o", markeredgecolor=couleur,
                     markersize=2*self.__canvas__.taille["o"], linewidth=epaisseur)
            plot.zorder = niveau
        elif debut is False:
            arc = self.rendu.arc(x, y, vec_deb)
            plot.set_data(*arc.get_data()) # � TESTER !!
            plot.set(visible=True, color=couleur, linewidth=epaisseur, marker="")
            plot.zorder = niveau
        else:
            plot.set_visible(False)

        # Fin de la courbe
        plot = self._representation[-1]
        x, y = self.__points[-1].coordonnees
        a, b = self.__points[-2].coordonnees
        if vec_fin is None:
            vec_fin = (a - x, b - y)
        if fin is True:
            plot.set_data((x,), (y,))
            plot.set(visible=True, color=couleur, marker="o", markeredgecolor=couleur,
                     markersize=2*self.__canvas__.taille["o"], linewidth=epaisseur)
            plot.zorder = niveau
        elif fin is False:
            arc = self.rendu.arc(x, y, vec_fin)
            plot.set_data(*arc.get_data()) # � TESTER !!
            plot.set(visible=True, color=couleur, linewidth=epaisseur, marker="")
            plot.zorder = niveau
        else:
            plot.set_visible(False)








class Interpolation_lineaire(Interpolation_generique):
    u"""Une interpolation lin�aire.

    Interpolation entre les points donn�s par des segments joints (courbe de classe C0).
    """

    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        if styles.get("points", None):
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
        Interpolation_generique.__init__(self, *points, **styles)

    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne() for i in xrange(n + 1)]

        self._xarray = array([])
        self._yarray = array([])

        if n < 2:
            return

        pas = self.__canvas__.pas()

        for i in xrange(n - 1):
            plot = self._representation[i]
            x1, y1 = self.__points[i].coordonnees
            x2, y2 = self.__points[i+1].coordonnees
            plot.set_data(array((x1, x2)), array((y1, y2)))
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
            plot.zorder = niveau
            # TODO: am�liorer l'algo de d�tection (notamment si l'�chelle
            # sur les 2 axes n'est pas la m�me).
            # Utiliser l'algorithme des segments.
            if abs(y2 - y1) < abs(x2 - x1):
                x_array = arange(x1, x2, pas if x1 < x2 else -pas)
                a = (y2 - y1)/(x2 - x1)
                b = y1 - a*x1
                y_array = a*x_array + b
            elif abs(y2 - y1) > contexte['tolerance']:
                y_array = arange(y1, y2, pas if y1 < y2 else -pas)
                a = (x2 - x1)/(y2 - y1)
                b = x1 - a*y1
                x_array = a*y_array + b
            else:
                continue
            self._xarray = append(self._xarray, x_array)
            self._yarray = append(self._yarray, y_array)

        self._affiche_extremites()






class Interpolation_quadratique(Interpolation_generique):
    u"""Une interpolation quadratique.

    Interpolation des points donn�s par une courbe polynomiale par morceaux, et de classe C1.
    Pour chaque morceau, x(t)=at�+bt+c et y(t)=dt�+et+f, o� t appartient � [0;1].
    """
    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        if "points" in styles:
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
        Interpolation_generique.__init__(self, *points, **styles)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne() for i in xrange(n + 1)]

        self._xarray = array([])
        self._yarray = array([])

        if n < 2:
            return

        pas = self.__canvas__.pas()
        t = fullrange(0, 1, pas)
        for i in xrange(n - 1):
            plot = self._representation[i]
            x0, y0 = self.__points[i].coordonnees
            x1, y1 = self.__points[i+1].coordonnees
            if i == 0:
                dx0, dy0 = x1 - x0, y1 - y0
            a, b, c = x1 - dx0 - x0, dx0, x0
            d, e, f = y1 - dy0 - y0, dy0, y0
            u = (a*t + b)*t + c
            v = (d*t + e)*t + f
            plot.set_data(u, v)
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
            plot.zorder = niveau

            dx0 = 2*a + b
            dy0 = 2*d + e

            self._xarray = append(self._xarray, u)
            self._yarray = append(self._yarray, v)

        self._affiche_extremites(vec_fin = (dx0, dy0))






class Interpolation_cubique(Interpolation_generique):
    u"""Une interpolation cubique.

    Interpolation des points donn�s par une courbe polynomiale par morceaux, de vecteur tangent horizontal aux sommets, et de classe C1 en g�n�ral (ie. si x_n!=x_{n-1}).
    Pour chaque morceau, x(t)=at^3+bt^2+ct+d et y(t)=et^3+ft^2+gt+h, o� t appartient � [0;1], et y'(0)=y'(1)=0.
    """

    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        if "points" in styles:
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
        Interpolation_generique.__init__(self, *points, **styles)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        courbure = self.style("courbure")
        if courbure is None:
            courbure = 1
        if not self._representation:
            self._representation = [self.rendu.ligne() for i in xrange(n + 1)]

        self._xarray = array([])
        self._yarray = array([])

        if n < 2:
            return

        pas = self.__canvas__.pas()
        t = fullrange(0, 1, pas)
        for i in xrange(n - 1):
            plot = self._representation[i]
            x0, y0 = self.__points[i].coordonnees
            x1, y1 = self.__points[i+1].coordonnees
            if i == 0:
                dx0 = x1 - x0
                dy0 = y1 - y0
            else:
                dx0 = courbure*abs(x1 - x0)
                if dx1 != 0:
                    dy0 = dy1/dx1*dx0
                else:
                    dx0 = dx1
                    dy0 = dy1
            if i < n - 2:
                x2, y2 = self.__points[i+2].coordonnees
                if cmp(y0, y1) == cmp(y1, y2):
                    dy1 = y2 - y0
                    dx1 = x2 - x0
                else:
                    dy1 = 0
                    dx1 = courbure*abs(x1 - x0)
            else:
                dy1 = y1 - y0
                dx1 = x1 - x0
            a = 2*(x0 - x1) + dx0 + dx1
            b = 3*(x1 - x0) -2*dx0 - dx1
            c = dx0
            d = x0
            e = 2*(y0 - y1) + dy0 + dy1
            f = 3*(y1 - y0) -2*dy0 - dy1
            g = dy0
            h = y0
            u = ((a*t + b)*t + c)*t + d
            v = ((e*t + f)*t + g)*t + h
            plot.set_data(u, v)
            plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
            plot.zorder = niveau

            self._xarray = append(self._xarray, u)
            self._yarray = append(self._yarray, v)

        self._affiche_extremites(vec_deb = (dx0, dy0), vec_fin = (dx1, dy1))


class Interpolation_polynomiale_par_morceau(Interpolation_generique):
    u"""Une courbe d'interpolation polynomiale par morceaux.
    Elle utilise l'interpolation par morceau de scipy pour construire la fonction
    c'est la classe scipy.interpolate.PiecewisePolynomial

    elle passe par les points (xl, yl) et avec le nombre derive dans derivl � 
    l'abscisse xl.

    exemple::

    >>> A = Point(-1,-2)
    >>> B = Point(2,1)
    >>> C = Point(8,-3)
    >>> d = Interpolation_polynomiale_par_morceau(A,B,C, derivees=[-1,0.5,2])
    
    :type derivee: list
    :param derivee: value of the diff number at each point
    
    :rtype : numpy.lib.polynomial

    """
    points = __points = Arguments("Point_generique")

    def __init__(self, *points, **styles):
        self.__derivees = derivees = styles.pop('derivees', len(points)*[0])
        debut = styles.pop("debut", True)
        fin = styles.pop("fin", True)
        if styles.get("points", None):
            points = styles.pop("points")
        self.__points = points = tuple(Ref(pt) for pt in points)
        # en test: creation des tangentes: dictionnaire
        # key: nom du point, value: objet Tangente_courbe
        self.__tangentes = []
        # boucle avec ruse enumerate 
        # cf http://docs.python.org/tutorial/datastructures.html#dictionaries
        for i, P in enumerate(points):
            dico = {'point': P, 'cdir': self.__derivees[i]}
            self.__tangentes.append(Tangente_courbe(**dico))
 
        self.__debut = debut = Ref(debut)
        self.__fin = fin = Ref(fin)
        Interpolation_generique.__init__(self, *points, **styles)

    def _poly_inter(self, xl, yl, derivl):
        u"""Fonction wrapper vers la fonction de scipy

        """
        yl_cum = [[yl[i], derivl[i]] for i in range(len(yl))]
        return PiecewisePolynomial(xl, yl_cum)


    def _creer_figure(self):
        n = len(self.__points)
        couleur = self.style("couleur")
        niveau = self.style("niveau")
        style = self.style("style")
        epaisseur = self.style("epaisseur")
        if not self._representation:
            self._representation = [self.rendu.ligne()]

        if n < 2:
            return
        #interpol doit �tre recalcul� � chaque mise � jour
        self.xl = [P[0] for P in self.__points]
        self.yl = [P[1] for P in self.__points]
        self.interpol = self._poly_inter(self.xl, self.yl, self.__derivees)
        # de m�me les tangentes sont recalcul�es
        # il doit y avoir moyen de faire moins de calculs
        self.__tangentes = []
        for i in range(len(self.__points)):
            self.__tangentes.append(Tangente_courbe(point = self.__points[i],\
                                                        cdir = self.__derivees[i]))
            #self.__tangentes[i]._creer_figure()
 
        
        pas = self.__canvas__.pas()
        plot = self._representation[0]
        x1, y1 = self.__points[0].coordonnees
        x2, y2 = self.__points[-1].coordonnees
        xarray = arange(x1, x2, pas)
        yarray = self.interpol(xarray)
        plot.set_data(xarray, yarray)
        plot.set(color=couleur, linestyle=style, linewidth=epaisseur)
        plot.zorder = niveau
        self._xarray = xarray
        self._yarray = yarray
        
        #self._affiche_extremites()
