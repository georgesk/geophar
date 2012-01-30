# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)
from __future__ import with_statement

##--------------------------------------#######
#                Probabilités                 #
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



def repetition_experiences(_profondeur=3, _numeroter=True, **evenements):
    u"""Génère le code d'un arbre de probababilités correspondant à la répétition
    d'expériences aléatoires identiques et indépendantes.
    Typiquement, un schéma de Bernoulli.

    >>> from wxgeometrie.modules.probabilites import repetition_experiences
    >>> print(repetition_experiences())
    >A_1:0.5
    >>A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    >>&A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    >&A_1:0.5
    >>A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    >>&A_2:0.5
    >>>A_3:0.5
    >>>&A_3:0.5
    """
    #FIXME: rajouter des tests unitaires.
    if not evenements:
        evenements = {'A': '1/2', '&A': '1/2'}
    elif not any(isinstance(proba, basestring) for proba in evenements.itervalues()):
        if len(evenements) == 1:
            # On rajoute l'évènement complémentaire
            nom, proba = evenements.items()
            nom = (nom[1:] if nom.startswith('&') else nom)
            proba = 1 - proba
            evenements[nom] = proba
        else:
            total_probas = sum(evenements.itervalues())
            reste = 1 - total_probas
            if abs(reste) > 0.0000000001:  # param.tolerance
                if reste > 0:
                    evenements['?'] = reste
                else:
                    raise ValueError, "La somme des probabilites depasse 1."

    def key(nom):
        u"""Classe les évènements par ordre alphabétique, mais en plaçant les
        évènements contraires en dernier."""
        return nom.replace('&', '_')
    evenements_tries = sorted(evenements, reverse=True, key=key)
    lines = ['']
    for niveau in range(1, _profondeur + 1):
        prefixe = niveau*'>'
        suffixe = ('_' + str(niveau) if _numeroter else '')
        for i in range(len(lines), 0, -1):
            if lines[i - 1].startswith((niveau - 1)*'>'):
                for nom in evenements_tries:
                    proba = evenements[nom]
                    lines.insert(i, prefixe + nom + suffixe + ':' + str(proba))
            assert len(lines) < 10000
    return '\n'.join(lines).strip()
