# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

from pytest import XFAIL

#from tools.testlib import assertAlmostEqual
from wxgeometrie.geolib.tests.geotestlib import rand_pt
from tools.testlib import assertEqual
from wxgeometrie.geolib import Feuille, Segment, NOM

def test_Label_point():
    A = rand_pt()
    B = rand_pt()
    A.label("Position de l'hirondelle d'Afrique.")
    B.label(u"Position de l'hirondelle europ�enne.")
    assert(A.label() == "Position de l'hirondelle d'Afrique.")
    assert(B.label() == u"Position de l'hirondelle europ�enne.")
    A.label(mode=NOM)
    assert A.mode_affichage == NOM
    assert(A.label() == '')
    f = Feuille()
    f.objets.A = A
    assert A.feuille is f
    assert A.etiquette.feuille is f
    assertEqual(A.nom_latex, '$A$')
    assertEqual(A.label(), '$A$')
    A.renommer("A'")
    assertEqual(A.label(), "$A'$")
    A.renommer("A''")
    assertEqual(A.label(), "$A''$")
    f.objets["B'"] = (1, 2)
    assertEqual(f.objets["B'"].label(), "$B'$")


def test_Label_segment():
    f = Feuille()
    s = f.objets.s = Segment()
    assert s.label() == ''
    s.label('bonjour !')
    assert s.label() == 'bonjour !'
    s.label(mode=NOM)
    assertEqual(s.label(), r'$\mathscr{s}$')


@XFAIL
def test_Label_droite():
    raise NotImplementedError

@XFAIL
def test_Label_demidroite():
    raise NotImplementedError

@XFAIL
def test_Label_cercle():
    raise NotImplementedError

@XFAIL
def test_Label_arc_cercle():
    raise NotImplementedError

@XFAIL
def test_Label_polygone():
    raise NotImplementedError

@XFAIL
def test_Label_angle():
    raise NotImplementedError

def test_latex_incorrect():
    u"On teste le comportement en cas de code LaTeX incorrect."
    A = rand_pt()
    A.label('2$')
    assertEqual(A.label(), r'2\$')
    A.label('US$2.50')
    assertEqual(A.label(), r'US\$2.50')
    A.label('$M__i$')
    assertEqual(A.label(), r'\$M__i\$')
    A.label('2$')
