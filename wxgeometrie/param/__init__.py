# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

######################################
#
#    Param�tres du programme
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

from time import mktime
import sys, platform, os

from ..version import version, date_version, NOMPROG, NOMPROG2
from .modules import modules, modules_actifs, descriptions_modules
from .parametres import *

time_version = mktime(date_version + (0, 0, 0) + (0, 0, 0))
# Derni�re v�rification d'une �ventuelle mise � jour
time_verification = time_version


# D�tection de la configuration
plateforme = platform.system() #'Windows' ou 'Linux' par exemple.
repertoire = os.getcwd() # memorise le repertoire de lancement
python_version = float(sys.version[:3])
python_version_info = sys.version_info
py2exe = hasattr(sys, 'frozen') # le programme tourne-t-il en version "executable" ?

# Param�tres d�tect�s dynamiquement lors de l'ex�cution :
ecriture_possible = None
EMPLACEMENT = '' # le r�pertoire contenant wxgeometrie.pyw

# Les valeurs suivantes ne doivent pas �tre enregistr�es dans les pr�f�rences de l'utilisateur :
# - soit parce qu'il n'y aurait aucun sens � les sauver (__builtins__ par exemple)
# - soit parce qu'elles doivent �tre g�n�r�es dynamiquement

valeurs_a_ne_pas_sauver = (
'EMPLACEMENT',
'GUIlib',
'ID',
'NOMPROG',
'NOMPROG2',
'__builtins__',
'charger_preferences',
'codage_des_angles',
'codage_des_lignes',
'date_version',
'dependances',
'descriptions_modules',
'ecriture_possible',
'emplacementsa_mettre_a_jour',
'familles_de_textes',
'getdefaultlocale',
'modules',
'os',
'pi',
'plateforme',
'platform',
'py2exe',
'python_min',
'python_version',
'python_version',
'repertoire',
'styles_a_ne_pas_copier',
'styles_a_signification_variable',
'styles_de_angles',
'styles_de_lignes',
'styles_de_points',
'styles_de_textes',
'time_version',
'types_de_hachures',
'valeurs_a_ne_pas_sauver',
'version',
)

# IMPORTANT !
# les dictionnaires pouvant comporter de nouvelles cl�s lors de la sortie d'une nouvelle version doivent �tre mis � jour :
a_mettre_a_jour = (
'angles',
'arcs',
'arcs_orientes',
'aretes',
'boutons',
'cercles',
'champs',
'codage',
'cotes',
'courbes',
'defaut_objets',
'droites',
'interpolations',
'labels',
'modules_actifs',
'points',
'points_deplacables',
'polyedres',
'polygones',
'segments',
'taille',
'textes',
'vecteurs',
'widgets',
)

del os, platform, sys

print(u'Import des param�tres termin�.')
