# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                    Suites                   #
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

from PyQt4.QtGui import (QPushButton, QWidget, QLabel, QSpinBox,
                         QHBoxLayout, QVBoxLayout,
                         QLineEdit, QComboBox, QFrame,
                         )

from ...GUI.qtlib import MyMiniFrame
from ...geolib import Point, Segment, Droite, RIEN, TEXTE
from ...pylib import eval_safe


class CreerSuite(MyMiniFrame):
    def __init__(self, parent):
        MyMiniFrame.__init__(self, parent, u"Repr�senter une suite")
        ##self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS )
        self.parent = parent
        self._param_ = self.parent._param_
        ##p = self.panel = QWidget(self)

        self.sizer = sizer = QVBoxLayout()
        sizer.addWidget(QLabel(u"Choisissez le mode de g�n�ration de la suite :"))
        self.mode = QComboBox()
        self.mode.addItems([u"u(n+1)=f(u(n))", u"u(n)=f(n)"])
        self.mode.setCurrentIndex(0)
        self.mode.currentIndexChanged.connect(self.EvtChoixMode)
        sizer.addWidget(self.mode)

        f = QHBoxLayout()
        f.addWidget(QLabel(u"Choisissez la fonction f :"))
        self.fonction = QComboBox()
        self.fonction.addItems(["Y" + str(i+1) for i in xrange(self.parent.nombre_courbes)])
        self.fonction.setCurrentIndex(0)
        self.fonction.currentIndexChanged.connect(self.EvtChoixFonction)
        f.addWidget(self.fonction)
        sizer.addLayout(f)

        start = QHBoxLayout()
        start.addWidget(QLabel(u"Commencer pour n ="))
        self.n0 = QSpinBox()
        self.n0.setRange(0, 1000000)
        self.n0.setValue(0)
        start.addWidget(self.n0)
        sizer.addLayout(start)

        terme = QHBoxLayout()
        self.label_init = QLabel(u"Terme initial :")
        terme.addWidget(self.label_init)
        self.un0 =  QLineEdit("1")
        self.un0.setMinimumWidth(100)
        terme.addWidget(self.un0)
        sizer.addLayout(terme)

        ligne = QFrame()
        ligne.setFrameStyle(QFrame.HLine|QFrame.Raised)
        ##sizer.addWidget(wx.StaticLine(p, -1, style=wx.LI_HORIZONTAL), 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        nbr = QHBoxLayout()
        nbr.addWidget(QLabel(u"Construire les"))
        self.termes = QSpinBox()
        self.termes.setRange(0, 100)
        self.termes.setValue(5)
        nbr.addWidget(self.termes)
        nbr.addWidget(QLabel(u"premiers termes."))
        sizer.addLayout(nbr)

        ligne = QFrame()
        ligne.setFrameStyle(QFrame.HLine|QFrame.Raised)

        sizer.addWidget(ligne)

        #p.SetSizer(sizer)
        boutons = QHBoxLayout()
        fermer = QPushButton(u"Fermer")
        boutons.addWidget(fermer)
        lancer = QPushButton(u"Cr�er")
        boutons.addWidget(lancer)
        fermer.clicked.connect(self.close)
        lancer.clicked.connect(self.Creer)
        sizer.addLayout(boutons)

        self.setLayout(sizer)
        ##self.SetClientSize(p.GetSize())





    def Creer(self):
##        self.parent.creer_feuille() # nouvelle feuille de travail
        # style des lignes :
        style, epaisseur = self._param_.style_suites_recurrentes
        kw_lignes = {"style": style, "epaisseur": epaisseur}

        # Les suites s'enregistrent aupr�s du module traceur
#        if not hasattr(self.parent, "suites"):
#            self.parent.suites = {}

        objets = self.parent.feuille_actuelle.objets
        i = self.fonction.currentIndex()
        nom_courbe = 'Cf' + str(i + 1)

        if objets.has_key(nom_courbe):
            courbe = objets[nom_courbe]
            fonction = courbe.fonction
        elif self.parent.boites[i].text():
            self.parent.valider(i=i)
            courbe = objets[nom_courbe]
            fonction = courbe.fonction
        else:
            # TODO: afficher un vrai message d'erreur
            raise KeyError,  "courbe inexistante : %s" %nom_courbe


        if self.mode.currentIndex() == 0: # cas des suites d�finies par r�currence
            u0 = eval_safe(self.un0.text())
            n0 = self.n0.value()

            d = objets.suiteDroited = Droite(Point(0, 0), Point(1, 1))
            d.label("$y\ =\ x$")
            M = objets.suitePointM0 = Point(u0, 0)
            M.label("$u_%s$" %(n0))
#            self.parent.suites["u"] = [d, M]

            for i in xrange(self.termes.value() - 1):
                # (Attention, �a ne va pas marcher pour les fonctions d�finies par morceau)
                u1 = fonction(u0)
                N = Point(u0, u1, visible=self._param_.afficher_points_de_construction)
                N.etiquette.visible = False
                s = Segment(M, N, **kw_lignes)
                P = Point(0, u1)
                P.label("$u_%s$" %(i + n0 + 1))
                t = Segment(N, P, **kw_lignes)
                Q = Point(u1, u1, visible = self._param_.afficher_points_de_construction)
                Q.etiquette.visible = False
                r = Segment(P, Q, **kw_lignes)
                M = Point(u1, 0)
                M.label("$u_%s$" %(i + n0 + 1))
                #self.parent.suites[u"u"].append([M, N, P, s, t])
                setattr(objets, "SuitePointN" + str(i), N)
                setattr(objets, "suitePointP" + str(i), P)
                setattr(objets, "suitePointQ" + str(i), Q)
                setattr(objets, "suiteSegments" + str(i), s)
                setattr(objets, "suiteSegmentt" + str(i), t)
                setattr(objets, "suiteSegmentr" + str(i), r)
                setattr(objets, "suitePointM" + str(i + 1), M)
                a = Segment(Q, M, **kw_lignes)
                setattr(objets, "suiteSegmenta" + str(i), a)
                u0 = u1
            self.parent.canvas.zoom_auto()

        else:   # suites d�finies explicitement
            n0 = self.n0.text()
#            self.parent.suites[u"u"] = []
            for i in xrange(n0, n0 + self.termes.text()):
                yi = fonction(i)
                M = Point(i, 0)
                M.label(str(i))
                N = Point(i, yi)
                N.etiquette.visible = False
                P = Point(0, yi)
                P.label("$u_%s$" %i)
                s = Segment(M, N, **kw_lignes)
                t = Segment(N, P, **kw_lignes)
                setattr(objets, "suitePointM" + str(i), M)
                setattr(objets, "suitePointN" + str(i), N)
                setattr(objets, "suitePointP" + str(i), P)
                setattr(objets, "suiteSegments" + str(i), s)
                setattr(objets, "suiteSegmentt" + str(i), t)
            self.parent.canvas.zoom_auto()



    def EvtChoixMode(self, index):
        if index == 1:
            self.label_init.hide()
            self.un0.hide()
        else:
            self.un0.show()
            self.label_init.show()


    def EvtChoixFonction(self, index):
        for i in xrange(self.parent.nombre_courbes):
            self.parent.boites[i].setChecked(i==index)
