# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

##--------------------------------------#######
#                 Geometre                    #
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

from PyQt4.QtGui import (QVBoxLayout, QLabel, QWidget,)

from ...pylib import path2
from ...GUI.menu import MenuBar
from ...GUI.panel import Panel_simple


class AccueilMenuBar(MenuBar):
    def __init__(self, panel):
        MenuBar.__init__(self, panel)
        self.ajouter(u"Fichier", [u"ouvrir"], ['session'], None, [u"quitter"])
        self.ajouter(u"Outils", [u"options"])
        self.ajouter(u"?")


class Accueil(Panel_simple):

    titre = u"Bienvenue !" # Donner un titre � chaque module

    def __init__(self, *args, **kw):
        Panel_simple.__init__(self, *args, **kw)
        sizer = QVBoxLayout()

        newtab = path2("%/wxgeometrie/images/newtab3.png")
        closetab = path2("%/wxgeometrie/images/closetab.png")
        texte = u"""
        <html><head/>
        <body style='font-size:12pt;'>
        <table bgcolor='#FFFCD6' style='border-color:#FFCF8C;border-style:solid;'>
        <tr><td style='padding:15px;margin:15px;'>
        <p><h2 align='center'>Bienvenue dans G�ophar !</h2></p>
        <br/>
        <p><i>Voici quelques indications pour bien commencer.</i></p>
        <p>En haut de la fen�tre, vous apercevez deux boutons.</p>
        <p></p>
        <ul><li style="margin-top:10px;">
        Le bouton <img src="%(newtab)s"/> a deux usages :
        <ul>
        <li style="margin-top:10px;">
        <b>activer les diff�rents modules</b> : calculatrice, traceur de
        courbes, g�om�trie dynamique...
        <br/>
        Les modules que vous activez le resteront au prochain d�marrage.
        </li>
        <li style="margin-top:10px;">
        <b>restaurer la session pr�c�dente</b>.<br/>
        Vous pouvez ainsi reprendre vos calculs interrompus, votre figure
        � moiti� achev�e... bref, tout votre travail en cours avant la fermeture du
        logiciel.
        </li>
        </ul>
        </li>
        <li style="margin-top:10px;">
        Le bouton <img src="%(closetab)s"/> sert, � l'inverse,
        � <b>fermer un module</b>.
        <br/>
        Fermer les modules que vous n'utilisez pas permet un d�marrage plus
        rapide de G�ophar.
        </li>
        </ul>
        <br/>
        </td></tr></table>
        </body></html>""" % locals()

        label = QLabel(texte)
        label.setWordWrap(True)
        sizer.addWidget(label)
        sizer.addStretch()
        self.setLayout(sizer)
