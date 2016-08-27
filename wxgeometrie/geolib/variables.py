# -*- coding: utf-8 -*-

##--------------------------------------#######
#                  Variable                   #
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

import re, time

from sympy import Symbol, Basic, sympify

from .objet import Ref, Argument, Objet, Objet_numerique, TYPES_REELS,\
                   contexte
from ..pylib import property2, print_error, fullrange, is_in
from ..mathlib.parsers import VAR_NOT_ATTR, NBR_SIGNE
from .. import param


class Variable_generique(Objet_numerique):
    """Une variable générique.

    Usage interne : la classe mère pour tous les types de variables."""

    _prefixe_nom = "k"
    _style_defaut = param.variables

    def __init__(self, **styles):
        Objet.__init__(self,  **styles)

    @staticmethod
    def _convertir(objet):
        "Convertit un objet en variable."
##        if isinstance(objet, Variable):   #  Inutile (?)
##            return objet.copy()
        return Variable(objet)


class Variable(Variable_generique):
    """Une variable libre.

    Une variable numérique ; l'argument peut être un nombre, ou une expression sous forme de chaine de caractères.
    Exemple: Variable(17.5), Variable('AB.longeur+1').
    Dans ce dernier cas, il est nécessaire qu'une feuille de travail soit définie.

    Note : ne pas définir directement l'attribut __contenu !"""

    # Mise en cache de la valeur
    __val_cache = __val_cache_approche = None
    # Utilisé par la classe `Formule`:
    _cache_formule = None

    # RE correspondant à un nom de variable (mais pas d'attribut)
    __re = re.compile('(' + VAR_NOT_ATTR + ')')

    def _set_contenu(self, value):
        if isinstance(value, Variable):
            if value.feuille is not None:
                value.feuille = self.feuille
            if value._Variable__fonction is None:
                return value.contenu
            return value.val
        elif isinstance(value, str):
            value = value.replace(" ","")
            # Si c'est un nombre:
            if not "." in value:
                try:
                    symp = sympify(value)
                    if not symp.atoms(Symbol):
                        value = symp
                except AttributeError:
                    pass
            elif re.match(NBR_SIGNE + "$", value):
                value = eval(value, {})
        elif isinstance(value, Basic):
            if not value.is_real:
                raise RuntimeError("La variable doit etre reelle.")
        return value


    __contenu = Argument(TYPES_REELS + (str,), None,  _set_contenu, defaut = 0)

    def __init__(self, contenu = 0, **styles):
        Variable_generique.__init__(self,  **styles)
        self.__liste = []
        self.__fonction = None
        self.__contenu = contenu = Ref(contenu)

    def _test_dependance_circulaire(self, valeur):
        """Provoque une erreur si l'objet se retrouve dépendre de lui-même avec la nouvelle valeur.

        Retourne une liste composée alternativement d'instructions et d'objets de la feuille,
        et un ensemble constitué des objets de la feuille mis en jeu dans le code.
        (... à documenter ...)"""
        if isinstance(valeur, Variable):
            valeur = valeur.contenu
        if isinstance(valeur, str) and self.feuille is not None:
            liste = re.split(self.__re, valeur)
            ensemble = set()
            for i in range(1, len(liste), 2):
                obj = self.feuille.objets[liste[i]]
                if isinstance(obj, Objet):
                    liste[i] = obj
                    ensemble.add(obj)
                    if self is obj or is_in(self, obj._ancetres()):
                        print(self, end=' ')
                        raise RuntimeError("Definition circulaire dans %s : l'objet %s se retrouve dependre de lui-meme." %(self, obj))
            return liste, ensemble
        return None, None


    def _compile(self,  liste, ensemble):
        """Compile l'expression stockée dans la variable ; les arguments sont les valeurs retournées par '_test_dependance_circulaire'.

        La compilation doit toujours avoir lieu à la fin de la procédure de redéfinition de la variable,
        car elle ne doit être exécutée que si la redéfinition de la variable va effectivement avoir lieu,
        c'est-à-dire si tout le processus précédent s'est exécuté sans erreur."""
        if self._type == "compose" and self.feuille is not None:
##            re.findall(self.__re,  self.valeur)
            self.__liste = liste
            self.__fonction = eval("lambda:" + self.__contenu, self.feuille.objets)
            # on supprime la variable de la liste des vassaux pour les objets dont elle ne dépendra plus desormais:
            for objet in self._parents:
                objet.enfants.remove(self)
            self._parents = ensemble
            self._modifier_hierarchie()
            for objet in self._parents:   # l'objet est vassal de chacun des objets dont il depend
                objet.enfants.append(self)
        else:
            for objet in self._parents:
                objet.enfants.remove(self)
            self._parents = set()
            self._modifier_hierarchie()
            self.__liste = []
            self.__fonction = None


    @property2
    def contenu(self, value = None):
        if value is None:
            if self.__liste: # variable contenant une expression compilée
                # On regénère l'expression à partir de l'expression compilée.
                # C'est important, car certains objets de la feuille peuvent avoir changé de nom entre temps.
                valeur = ""
                for elt in self.__liste:
                    if isinstance(elt, Objet):
                        valeur += elt.nom
                    else:
                        valeur += elt
                return valeur
            else:
                return self.__contenu
        else:
            args = self._test_dependance_circulaire(value)
            self.__contenu = value
            self._compile(*args)


    def _get_valeur(self):
        # cf. self._conditions_existence
        return self.__val_cache if contexte['exact'] else self.__val_cache_approche


    def _set_valeur(self, valeur):
        self.contenu = valeur

    def _set_feuille(self):
        self._compile(*self._test_dependance_circulaire(self.__contenu))
        self.perime()

    @property
    def _type(self):
        return isinstance(self.__contenu, str) and "compose" or "simple"

    def _recenser_les_parents(self):
#        warning("'_recenser_les_ancetres' n'a aucun effet pour une variable.")
        self._modifier_hierarchie()


    def _conditions_existence(self): # conditions specifiques pour que l'objet existe, a definir pour chaque objet
        if self._type == "compose":
            try:
                self.__val_cache = self.__fonction()
                if isinstance(self.__val_cache, Variable):
                    self.__val_cache = self.__val_cache.val
            except Exception:
                if param.verbose:
                    print_error("Impossible de déterminer la valeur de la variable " + self.nom + repr(self))
                return False
        else:
            self.__val_cache = self.contenu
        try:
            self.__val_cache_approche = float(self.__val_cache)
        except TypeError:
            print_error("Variable de type incorrect.")
            return False
        return True


    def __str__(self):
        return str(self.contenu)

    def __repr__(self, styles=True):
        return repr(self.contenu)

    def _definition(self):
        if self._type == "compose":
            return repr(self.contenu)
        else:
            return str(self.contenu)



    def _update(self, objet):
        if not isinstance(objet, Variable):
            objet = self._convertir(objet)
        if isinstance(objet, Variable):
            if objet.feuille is not None:
                objet.feuille = self.feuille
            if objet._Variable__fonction is None:
                self.contenu = objet.contenu
            else:
                self.val = objet.val
        else:
            raise TypeError("l'objet n'est pas une variable.")



    def varier(self, debut = 0, fin = 1, pas = 0.02, periode = 0.03):
        if self.feuille is not None:
            self.feuille.start()
            for i in fullrange(debut, fin, pas):
                t = time.clock()
                self.val = i
                while time.clock() < t + periode:
                    self.souffler()
                    if self.feuille._stop:
                        break
                self.souffler()
                if self.feuille._stop:
                    break


### Addition et multiplication liées
### ------------------------------------------------

### Est-ce encore bien utile ?

##    def add(self, y):
##        u"Addition liée (le résultat est une variable qui reste toujours égale à la somme des 2 valeurs)."
##        if self._type == "simple":
##            if isinstance(y, TYPES_NUMERIQUES) or (isinstance(y, Variable) and y._type == "simple"):
##                return Variable(self + y)
##        var = Variable("(%s)+(%s)" %(self, y))
##        var.__feuille__ = self.__feuille__
##        return var

##    def mul(self, y):
##        u"Multiplication liée (le résultat est une variable qui reste toujours égale au produit des 2 valeurs)."
##        if self._type == "simple":
##           if isinstance(y, TYPES_NUMERIQUES) or (isinstance(y, Variable) and y._type == "simple"):
##                return Variable(self * y)
##        var = Variable("(%s)*(%s)" %(self, y))
##        var.__feuille__ = self.__feuille__
##        return var


class Rayon(Variable_generique):
    """Le rayon d'un cercle.

    >>> from wxgeometrie.geolib import Cercle, Rayon
    >>> c = Cercle((0, 0), 1)
    >>> float(c.rayon)
    1.0
    >>> r = Rayon(c)
    >>> float(r)
    1.0
    >>> c.rayon = 2
    >>> float(r)
    2.0
    """

    __cercle = cercle = Argument("Cercle_Arc_generique")

    def __init__(self, cercle, **styles):
        self.__cercle = cercle = Ref(cercle)
        Variable_generique.__init__(self, **styles)

    def _get_valeur(self):
        return self.__cercle.rayon



class Mul(Variable_generique):
    """Le produit de deux variables."""

    __var1 = var1 = Argument(Variable_generique)
    __var2 = var2 = Argument(Variable_generique)

    def __init__(self, var1, var2, **styles):
        self.__var1 = var1 = Ref(var1)
        self.__var2 = var2 = Ref(var2)
        Variable_generique.__init__(self, **styles)

    def _get_valeur(self):
        return self.__var1.val*self.__var2.val


class Add(Variable_generique):
    """La somme de deux variables."""

    __var1 = var1 = Argument(Variable_generique)
    __var2 = var2 = Argument(Variable_generique)

    def __init__(self, var1, var2, **styles):
        self.__var1 = var1 = Ref(var1)
        self.__var2 = var2 = Ref(var2)
        Variable_generique.__init__(self, **styles)

    def _get_valeur(self):
        return self.__var1.val + self.__var2.val


class Variable_affichage(Variable_generique):
    """La classe mère des paramètres d'affichage (xmin, xmax, ...)"""
    parametre = NotImplemented

    # Inutile de les enregistrer sur la feuille, puisqu'elles ne font que
    # pointer vers la fenêtre d'affichage qui est déjà enregistrée dans la
    # feuille.
    _enregistrer_sur_la_feuille = False

    def _get_valeur(self):
        """Retourne la valeur du paramètre d'affichage (xmin ou xmax ou ...)

        Si un canvas est défini, la valeur retournée est prise sur le canvas,
        sinon, elle est récupérée depuis la feuille.
        Les deux valeurs ne coïncident pas forcément si une contrainte est
        imposée à l'affichage (par exemple, un repère orthonormé).
        Dans ce cas, il se peut que l'affichage à l'écran (canvas) dépasse
        la taille de la fenêtre de la feuille."""
        if self.feuille.canvas:
            return getattr(self.feuille.canvas, self.parametre)
        return getattr(self.feuille, self.parametre)

    def __repr__(self, styles=True):
        return repr(self._get_valeur())

    def __str__(self):
        return str(self._get_valeur())

    def _update(self, objet):
        setattr(self.feuille, self.parametre, objet)

    _set_valeur = _update


class XMinVar(Variable_affichage):
    """Le minimum de la fenêtre en abscisse."""
    parametre = 'xmin'


class XMaxVar(Variable_affichage):
    """Le maximum de la fenêtre en abscisse."""
    parametre = 'xmax'


class YMinVar(Variable_affichage):
    """Le minimum de la fenêtre en ordonnée."""
    parametre = 'ymin'


class YMaxVar(Variable_affichage):
    """Le maximum de la fenêtre en ordonnée."""
    parametre = 'ymax'


class Pixel_unite(Variable_generique):
    """Correspond à un pixel."""

    # Inutile d'enregistrer ces variables sur la feuille, puisqu'elles ne font que
    # pointer vers le canvas.
    _enregistrer_sur_la_feuille = False

    def _set_valeur(self):
        raise AttributeError

    def __repr__(self, styles=True):
        return repr(self._get_valeur())

    def __str__(self):
        return str(self._get_valeur())


class Dpx(Pixel_unite):
    """Un pixel unité en abscisse."""

    def _get_valeur(self):
        if self.feuille:
            return self.feuille.dpix2coo(1, 0)[0]


class Dpy(Pixel_unite):
    """Un pixel unité en ordonnée."""

    def _get_valeur(self):
        if self.feuille:
            return self.feuille.dpix2coo(0, -1)[1]

