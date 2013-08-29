#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#           Mathlib 2 (sympy powered)         #
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


from functools import partial

from sympy import (exp, ln, tan, pi, Symbol, oo, solve, Wild, sympify,
                    Add, Mul, sqrt,
                    )
from .intervalles import Intervalle, vide, Union, R
from .internal_functions import extract_var, count_syms, is_pos, is_var, is_neg
from .custom_functions import floats2rationals
from ..pylib import split_around_parenthesis
from .sympy_functions import factor, solve as solve_
from .. import param






def nul(expression, variable=None, intervalle=True, ensemble='R'):
    u"""Retourne l'ensemble sur lequel une expression à variable réelle est nulle.

    :param expression: une expression mathématique
    :type expression: string
    :param variable: un nom de variable
    :type variable: string
    :param intervalle: returne le résultat sous forme d'intervalle
    :type intervalle: bool
    :param ensemble: dans quel ensemble l'équation doit être résolue ('R' ou 'C')
    :type ensemble: string

    .. note:: Si la variable n'est pas précisée, elle est déduite de l'expression.
              (S'il y a plusieurs variables, une des variables est choisie au hasard.)

    """
    if ensemble == 'C':
        intervalle = False
    if variable is None:
        variable = extract_var(expression)
    expression = factor(expression, variable, ensemble=ensemble, decomposer_entiers=False)
    if expression.is_Mul:
        facteurs = expression.args
    else:
        facteurs = [expression]

    solutions = (vide if intervalle else set())

    for facteur in facteurs:
        liste_solutions = solve_(facteur, variable, ensemble=ensemble)
        if intervalle:
            solutions += Union(*liste_solutions)
        else:
            solutions.update(liste_solutions)
    return solutions


def ensemble_definition(expression, variable = None):
##    print expression, variable
    if variable is None:
        variable = extract_var(expression)
    ens_def = R
    if hasattr(expression, "is_Add") and expression.is_Add:
        for terme in expression.args:
            ens_def *= ensemble_definition(terme, variable)
        return ens_def
##    try:
##        expression = sympy_functions.factor(expression, variable, "R", decomposer_entiers = False)
##    except (NotImplementedError, TypeError):
##        if param.debug:
##            print "Warning: Factorisation impossible de ", expression
    if hasattr(expression, "subs"):
        old_variable = variable
        variable = Symbol("_tmp",real=True)
        expression = expression.subs({old_variable:variable})
    if hasattr(expression, "is_Pow") and expression.is_Pow:
        base, p = expression.as_base_exp()
        if p.is_integer:
            if p >= 0:
                return ensemble_definition(base, variable)
            else:
                return ensemble_definition(base, variable) - nul(base, variable)
        elif p.is_rational:
            n, d = p.as_numer_denom()
            if abs(n) == 1 and not d.is_even:
                if p >= 0:
                    return ensemble_definition(base, variable)
                else:
                    return ensemble_definition(base, variable) - nul(base, variable)
            else:
                if p >= 0:
                    return positif(base, variable)
                else:
                    return positif(base, variable, strict = True)
        else:
            if p >= 0:
                return positif(base, variable)
            else:
                return positif(base, variable, strict = True)
    elif hasattr(expression, "is_Mul") and expression.is_Mul:
        for facteur in expression.args:
            ens_def *= ensemble_definition(facteur, variable)
        return ens_def
    elif isinstance(expression, tan):
        arg = expression.args[0] # -pi/2 < arg < pi/2
        return positif(arg + pi/2, variable, strict = True)*positif(pi/2-arg, variable, strict = True)
    elif isinstance(expression, ln):
        arg = expression.args[0] # 0 < arg
        return positif(arg, variable, strict = True)
    return ens_def



def positif(expression, variable = None, strict = False):
    u"""Retourne l'ensemble sur lequel une expression à variable réelle est positive (resp. strictement positive)."""
    from .sympy_functions import factor
    # L'étude du signe se fait dans R, on indique donc à sympy que la variable est réelle.
    if variable is None:
        variable = extract_var(expression)
    if hasattr(expression, "subs"):
        old_variable = variable
        variable = Symbol("_tmp",real=True)
        expression = expression.subs({old_variable:variable})
    ens_def = ensemble_definition(expression, variable)
    try:
        expression = factor(expression, variable, "R", decomposer_entiers = False)
    except NotImplementedError:
        if param.debug:
            print "Warning: Factorisation impossible de ", expression
##    print "T455451", expression, variable
    if hasattr(expression, "is_Pow") and expression.is_Pow and expression.as_base_exp()[1].is_rational:
        base, p = expression.as_base_exp()
        # Le dénominateur ne doit pas s'annuler :
        if p < 0:
            strict = True
        if p.is_integer and p.is_even:
            if strict:
                return ens_def*(R - (positif(base, variable, strict = False) - positif(base, variable, strict = True)))
            else:
                return ens_def
        else:
            return ens_def*positif(base, variable, strict = strict)
    if hasattr(expression, "is_Mul") and expression.is_Mul:
        posit = R
        posit_nul = R
        for facteur in expression.args:
            # pos : ensemble des valeurs pour lequelles l'expression est positive
            # pos_nul : ensemble des valeurs pour lequelles l'expression est positive ou nulle
            pos = positif(facteur, variable, strict = True)
            pos_nul = positif(facteur, variable, strict = False)
            # posit : les deux sont strictements positifs, ou les deux sont strictements négatifs
            # posit_nul : les deux sont positifs ou nuls, ou les deux sont négatifs ou nuls
            posit, posit_nul = (posit*pos + (-posit_nul)*(-pos_nul))*ens_def, (posit_nul*pos_nul + (-posit)*(-pos))*ens_def

##            print "resultat", facteur, res
####            if res is NotImplemented:
####                return NotImplemented
##            # le résultat est positif si les deux facteurs sont positifs, ou si les deux facteurs sont négatifs:
##            resultat = resultat*res + (-resultat)*(-res)
        if strict:
            return posit
        else:
            return posit_nul
    if getattr(expression, "is_positive", None) is True: # > 0
        return ens_def
    if getattr(expression, "is_negative", None) is True: # < 0
        return vide
    if getattr(expression, "is_positive", None) is False and strict: # <= 0
        return vide
    if getattr(expression, "is_negative", None) is False and not strict: # >= 0
        return ens_def
    if getattr(expression, "is_zero", None) is True and not strict: # == 0
        return ens_def
    if isinstance(expression, (int, float, long)):
        if expression > 0 or (expression == 0 and not strict):
            return ens_def
        else:
            return vide
    # pas besoin de l'ensemble de définition pour les fonctions polynomiales
    if hasattr(expression, "is_polynomial") and expression.is_polynomial():
        P = expression.as_poly(variable)
        if P.degree() == 1:
            a, b = P.all_coeffs()
            if a > 0:
                return Intervalle(-b/a, +oo, inf_inclus = not strict)
            else: # a<0 (car a != 0)
                return Intervalle(-oo, -b/a, sup_inclus = not strict)
        elif P.degree() == 2:
            a, b, c = P.all_coeffs()
            d = b**2 - 4*a*c
            if d > 0:
                x1 = (-b - sqrt(d))/(2*a)
                x2 = (-b + sqrt(d))/(2*a)
                x1, x2 = min(x1, x2), max(x1, x2)
                if a > 0:
                    return Intervalle(-oo, x1, sup_inclus = not strict) + Intervalle(x2, +oo, inf_inclus = not strict)
                else: # a<0 (car a != 0)
                    return Intervalle(x1, x2, inf_inclus = not strict, sup_inclus = not strict)
            elif d == 0:
                x0 = -b/(2*a)
                if a > 0:
                    return Intervalle(-oo, x0, sup_inclus  = not strict) + Intervalle(x0, +oo, inf_inclus = not strict)
                else:
                    return Intervalle(x0, x0, sup_inclus  = not strict)
            else: # d < 0
               if a > 0:
                   return R
               else:
                   return vide

    # a*f(x)+b > 0 <=> f(x)+b/a > 0 pour a > 0, -f(x) - b/a > 0 pour a < 0
    if getattr(expression, "is_Add", False):
        args = expression.args
        if len(args) == 2:
            liste_constantes = []
            liste_autres = []
            for arg in args:
                if is_var(arg, variable):
                    liste_autres.append(arg)
                else:
                    liste_constantes.append(arg)
            if len(liste_autres) == 1:
                partie_constante = Add(*liste_constantes)
                partie_variable = liste_autres[0]
                if getattr(partie_variable, "is_Mul", False):
                    liste_facteurs_constants = []
                    liste_autres_facteurs = []
                    for facteur in partie_variable.args:
                        if is_var(facteur, variable):
                            liste_autres_facteurs.append(facteur)
                        else:
                            liste_facteurs_constants.append(facteur)
                    if liste_facteurs_constants:
                        facteur_constant = Mul(*liste_facteurs_constants)
                        autre_facteur = Mul(*liste_autres_facteurs)
                        if is_pos(facteur_constant):
                            return positif(autre_facteur + partie_constante/facteur_constant, variable, strict = strict)
                        elif is_neg(facteur_constant):
                            return ens_def*(R - positif(autre_facteur + partie_constante/facteur_constant, variable, strict = not strict))


    # Logarithme :
    if isinstance(expression, ln):
        return positif(expression.args[0] - 1, variable, strict = strict)
    # Résolution de ln(X1) + ln(X2) + ... + b > 0, où X1=f1(x), X2 = f2(x) ...
    if getattr(expression, "is_Add", False):
        args = expression.args
        liste_constantes = []
        liste_ln = []
        # Premier passage : on remplace a*ln(X1) par ln(X1**a)
        for arg in args:
            if getattr(arg, "is_Mul", False):
                liste_constantes = []
                liste_ln = []
                for facteur in arg.args:
                    if isinstance(facteur, ln) and is_var(facteur, variable):
                        liste_ln.append(facteur)
                    elif not is_var(facteur, variable):
                        liste_constantes.append(facteur)
##                print facteur, liste_constantes, liste_ln
                if len(liste_constantes) == len(arg.args) - 1 and len(liste_ln) == 1:
                    expression += ln(liste_ln[0].args[0]**Add(*liste_constantes)) - arg
##        print "Resultat 1er passage:", expression
        # Deuxième passage : ln(X1)+ln(X2)+b>0 <=> X1*X2-exp(-b)>0
        for arg in args:
            if isinstance(arg, ln) and hasattr(arg, "has_any_symbols") and arg.has(variable):
                liste_ln.append(arg)
            elif not hasattr(arg, "has_any_symbols") or not arg.has(variable):
                liste_constantes.append(arg)

        if liste_ln and len(liste_ln) + len(liste_constantes) == len(args):
            # ln(X1)+ln(X2)+b>0 <=> X1*X2-exp(-b)>0
            contenu_log = Mul(*(logarithme.args[0] for logarithme in liste_ln))
            contenu_cst = exp(- Add(*liste_constantes))
            return ens_def*positif(contenu_log - contenu_cst, variable, strict = strict)



    # Exponentielle
    # Résolution de a*exp(f(x)) + b > 0
    if getattr(expression, "is_Add", False):
        a_ = Wild('a')
        b_ = Wild('b')
        X_ = Wild('X')
        match = expression.match(a_*exp(X_) + b_)
        if match is not None and X_ in match:
            # Il faut tester si X_ est dans match, car on peut avoir a_=0, et
            # X_ non défini.
            a = match[a_]
            b = match[b_]
            X = match[X_]
            if  a != 0 and not a.has(variable) and not b.has(variable):
                if is_pos(b):
                    if is_pos(a):
                        return ens_def
                    elif is_neg(a):
                        # l'ensemble de définition ne change pas
                        return positif(- X + ln(-b/a), variable, strict = strict)
                elif is_neg(b):
                    if is_pos(a):
                        return positif(X - ln(-b/a), variable, strict = strict)
                    elif is_neg(a):
                        return vide

    # Cas très particulier : on utilise le fait que exp(x)>=x+1 sur R
    if getattr(expression, "is_Add", False):
        expr = expression
        changements = False
        for arg in expr.args:
            if isinstance(arg, exp):
                changements = True
                expr += arg.args[0] + 1 - arg
        if changements and (ens_def - positif(expr, variable, strict = strict) == vide):
            return ens_def

    # Sommes contenant des logarithmes :
    if getattr(expression, "is_Add", False):
        # Cas très particulier : on utilise le fait que ln(x)<=x-1 sur ]0;+oo[
        expr = expression
        changements = False
        for arg in expr.args:
            if isinstance(arg, ln):
                changements = True
                expr += arg.args[0] + 1 - arg
        if changements:
            try:
##                print "S458475",  -expr
                non_positif = positif(-expr, variable, strict = not strict) # complementaire
                (ens_def - positif(expr, variable, strict = not strict) == vide)
                if (ens_def - non_positif == vide):
                    return vide
            except NotImplementedError:
                pass

            # Somme contenant des logarithmes : si aucune autre méthode n'a fonctionné, on tente ln(a)+ln(b)>0 <=> a*b>1 (pour a>0 et b>0)
            expr = Mul(*(exp(arg) for arg in expression.args)) - 1
            try:
                return ens_def*positif(expr, variable, strict = strict)
            except NotImplementedError:
                pass


##    print "Changement de variable."
    # En dernier recours, on tente un changement de variable :
    tmp2 = Symbol("_tmp2", real=True)
    # changements de variables courants : x², exp(x), ln(x), sqrt(x), x³ :
    for X in (variable**2, variable**3, exp(variable), ln(variable), sqrt(variable)):
        expr = expression.subs(X, tmp2)
        # Si la nouvelle variable apparait une seule fois,
        # le changement de variable produirait une récurrence infinie !
        if variable not in expr.atoms() and count_syms(expr, X) > 1:
##            print "nouvelle variable:", X
            solution_temp = positif(expr, tmp2, strict = strict)
            solution = vide
            for intervalle in solution_temp.intervalles:
                sol = R
                a = intervalle.inf
                b = intervalle.sup
                if a != - oo:
                    sol *= positif(X - a, variable, strict = strict)
                if b != oo:
                    sol *= positif(b - X, variable, strict = strict)
                solution += sol
            return ens_def*solution
    raise NotImplementedError


def resoudre(chaine, variables=(), local_dict=None, ensemble='R'):
    u"""Résout une équation ou inéquation, rentrée sous forme de chaîne.


    """
    def evaluer(expression, local_dict=local_dict):
        if local_dict is None:
            # sympy se débrouille bien mieux avec des rationnels
            expression = sympify(expression, rational=True)
        else:
            expression = eval(expression, local_dict.globals, local_dict)
            # sympy se débrouille bien mieux avec des rationnels
            expression = floats2rationals(expression)
        return expression

    # Préformatage:
    chaine = chaine.replace(')et', ') et').replace(')ou', ') ou').replace('et(', 'et (').replace('ou(', 'ou (')
    chaine = chaine.replace("==", "=").replace("<>", "!=").replace("=>", ">=").replace("=<", "<=")

    if not variables:
        # Détection des variables dans l'expression
        arguments = chaine.split(',')
        variables = [Symbol(s.strip()) for s in arguments[1:]]

        if not variables:
            # Les variables ne sont pas explicitement indiquées.
            # On tente de les détecter.
            variables = set()
            chaine2tuple = arguments[0]
            for s in (' et ', ' ou ', '>=', '<=', '==', '!=', '=', '<', '>'):
                chaine2tuple = chaine2tuple.replace(s, ',')

            def find_all_symbols(e):
                s = set()
                if isinstance(e, tuple):
                    s.update(*(find_all_symbols(elt) for elt in e))
                else:
                    s.update(e.atoms(Symbol))
                return s
            variables = find_all_symbols(evaluer(chaine2tuple))

        chaine = arguments[0]

    ##print 'variables:', variables

    if len(variables) > 1:
        return systeme(chaine, local_dict = local_dict)

    assert len(variables) == 1
    variable = tuple(variables)[0]
#    fin = ",".join(arguments[1:])
#    if fin:
#        fin = "," + fin
    debut = ''
    _resoudre = partial(resoudre, variables=variables, ensemble=ensemble, local_dict=local_dict)
    while chaine:
        l = [s for s in split_around_parenthesis(chaine)]
        if len(l) == 3:
            if l[0].strip() == l[2].strip() == '':
                return _resoudre(chaine[1:-1])
            if ' et ' in l[0]:
                retour = chaine.split(' et ', 1)
                retour[0] = debut + retour[0]
                return _resoudre(retour[0]) & _resoudre(retour[1])
            elif ' ou ' in l[0]:
                retour = chaine.split(' ou ', 1)
                retour[0] = debut + retour[0]
                return _resoudre(retour[0]) | _resoudre(retour[1])
            chaine = l[2]
            debut += l[0] + l[1]
        else:
            if ' et ' in chaine:
                retour = chaine.split(' et ', 1)
                retour[0] = debut + retour[0]
                return _resoudre(retour[0]) & _resoudre(retour[1])
            elif ' ou ' in chaine:
                retour = chaine.split(' ou ', 1)
                retour[0] = debut + retour[0]
                return _resoudre(retour[0]) | _resoudre(retour[1])
            else:
                break
    chaine = debut + chaine

    if ">=" in chaine:
        gauche, droite = chaine.split(">=")
        if ensemble != 'R':
            print("Warning: can't solve in '%s', solving in 'R'." % ensemble)
        return positif(evaluer(gauche + "-(" + droite + ")"), variable)
    elif "<=" in chaine:
        gauche, droite = chaine.split("<=")
        if ensemble != 'R':
            print("Warning: can't solve in '%s', solving in 'R'." % ensemble)
        return positif(evaluer(droite + "-(" + gauche + ")"), variable)
    if ">" in chaine:
        gauche, droite = chaine.split(">")
        if ensemble != 'R':
            print("Warning: can't solve in '%s', solving in 'R'." % ensemble)
        return positif(evaluer(gauche + "-(" + droite + ")"), variable, **{"strict": True})
    elif "<" in chaine:
        gauche, droite = chaine.split("<")
        if ensemble != 'R':
            print("Warning: can't solve in '%s', solving in 'R'." % ensemble)
        return positif(evaluer(droite + "-(" + gauche + ")"), variable, **{"strict": True})
    elif "!=" in chaine:
        gauche, droite = chaine.split("!=")
        expression = evaluer(gauche + "-(" + droite + ")")
        if ensemble != 'R':
            print("Warning: can't solve in '%s', solving in 'R'." % ensemble)
        return ensemble_definition(expression, variable) - nul(expression, variable)
    elif "=" in chaine:
        gauche, droite = chaine.split("=")
        expression = evaluer(gauche + "-(" + droite + ")")
        return nul(expression, variable, ensemble=ensemble)
    else:
        raise TypeError, "'" + chaine + "' must be an (in)equation."


def systeme(chaine, variables = (), local_dict = None):
    chaine = chaine.replace("==", "=")
    if local_dict is None:
        evaluer = sympify
    else:
        def evaluer(expression, local_dict = local_dict):
            return eval(expression, local_dict.globals, local_dict)

    def transformer(eq):
        gauche, droite = eq.split("=")
        return evaluer(gauche + "-(" + droite + ")")

    if not variables:
        arguments = chaine.split(',')
        variables = tuple(Symbol(s.strip()) for s in arguments[1:])
        chaine = arguments[0]
    eqs = tuple(transformer(eq) for eq in chaine.split("et"))
    if not variables:
        variables = set()
        for eq in eqs:
            variables.update(eq.atoms(Symbol))
    return solve(eqs, *variables)

