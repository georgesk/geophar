# -*- coding: utf-8 -*-

##--------------------------------------##
#                  Onglets               #
##--------------------------------------##
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

import os
from webbrowser import open_new_tab
from functools import partial
from io import StringIO

from PyQt4.QtGui import QTabWidget, QToolButton, QIcon, QMessageBox, QFileDialog, \
                        QDialog, QPainter, QPrintDialog, QPrinter, QFont
from PyQt4.QtCore import Qt, QPoint, QByteArray, QRectF
from PyQt4.QtSvg import QSvgRenderer
import matplotlib.backend_bases as backend_bases

from .aide import About, Informations
from .animer import DialogueAnimation
from .contact import Contact
from .dialogues_geometrie import EditerObjet, SupprimerObjet
from .fenetre_options import FenetreOptions
from .inspecteur import FenCode
from .nouvelles_versions import Gestionnaire_mises_a_jour
from .proprietes_feuille import ProprietesFeuille
from .proprietes_objets import Proprietes
from .qtlib import PopUpMenu, png_pth
from . import dialogues_geometrie
from ..API.sauvegarde import FichierGEO, ouvrir_fichierGEO
from .. import param, modules, geolib
from ..param import NOMPROG
from ..pylib import print_error, debug, path2
from ..param.options import options as param_options


class Onglets(QTabWidget):

    _nom_fichier_session = ''

    def __init__(self, parent):
        self.parent = parent
        QTabWidget.__init__(self, parent)
        self.setStyleSheet("""
            QTabBar::tab:selected {
            background: white;
            border: 1px solid #C4C4C3;
            border-bottom-color: white; /* same as the pane color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 8ex;
            padding: 7px;
            }
            QStackedWidget {background:white}
            QTabBar QToolButton {
            background:white;
            border: 1px solid #C4C4C3;
            border-bottom-color: white; /* same as the pane color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            }
            """)
        self.setTabsClosable(False)
        self.setMovable(True)
        ##self.tabCloseRequested.connect(self.fermer_onglet)
#        palette = QPalette()
#        white = QColor(Qt.white)
#        palette.setColor(QPalette.Window, white)
#        palette.setColor(QPalette.Button, white)
#        palette.setColor(QPalette.WindowText, white)
#        self.setPalette(palette)

        ###############################
        # Creation de fonctions associees aux entrees du menu "Creer"
        self.creer = {}
        DG = dialogues_geometrie.__dict__
        dialogues = [(nom[8:], DG[nom]) for nom in DG if nom.startswith("Dialogue")]
        for dialogue in dialogues:
            def f(event = None, self = self, dialogue = dialogue[1]):
                self.creer_objet(dialogue)
            self.creer[dialogue[0]] = f
        ###############################

        # Bouton "Nouvel onglet"
        self.newTabButton = newTabButton = QToolButton(self)
        self.setCornerWidget(newTabButton, Qt.TopLeftCorner)
        newTabButton.setCursor(Qt.ArrowCursor)
        newTabButton.setAutoRaise(True)
        newTabButton.setIcon(QIcon(path2("%/wxgeometrie/images/newtab3.png")))
        newTabButton.clicked.connect(self.popup_activer_module)
        newTabButton.setToolTip("Activer un autre onglet")

        # Bouton "Fermer l'onglet"
        self.closeTabButton = closeTabButton = QToolButton(self)
        self.setCornerWidget(closeTabButton, Qt.TopRightCorner)
        closeTabButton.setCursor(Qt.ArrowCursor)
        closeTabButton.setAutoRaise(True)
        closeTabButton.setIcon(QIcon(path2("%/wxgeometrie/images/closetab.png")))
        closeTabButton.clicked.connect(partial(self.fermer_onglet, None))
        closeTabButton.setToolTip("Fermer l'onglet courant")

        self.gestionnaire_de_mises_a_jour = Gestionnaire_mises_a_jour(self)

        self._liste = [] # liste des onglets

        # Ajoute les differentes composantes :
        self.actualiser_liste_onglets()

        # Usage interne : le signal `.currentChanged` ne transmet pas le numéro de l'onglet
        # précédemment actif, il faut donc garder manuellement en mémoire l'onglet actif.
        self._ancien_onglet = None
        # adaptation du titre de l'application et du menu.
        self.currentChanged.connect(self.evt_changer)

        # Use the tabMoved signal of QTabBar. You can get the QTabBar used
        # in QTabWidget with the tabBar() method.
        self.tabBar().tabMoved.connect(self.evt_deplacer_onglet)


    # -------------------
    # Gestion des onglets
    # -------------------

    def popup_activer_module(self):
        """Affiche un menu permettant d'activer des modules."""
        menu = PopUpMenu("Module à activer", self, 'crayon')
        deja_charges = [onglet.__module__.split('.')[-1] for onglet in self]
        exercices = None
        for nom in param.modules:
            if nom not in deja_charges:
                titre = param.descriptions_modules[nom]['titre']
                if titre.startswith('Exercices - '):
                    if exercices is None:
                        exercices = menu.addMenu('Exercices')
                    action = exercices.addAction(titre[12:])
                else:
                    action = menu.addAction(titre)
                action.triggered.connect(partial(self.activer_module, nom, selectionner=True))
        menu.addSeparator()
        action = menu.addAction(QIcon(png_pth('reload')), "Restaurer la session précédente")
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.ChargerSessionPrecedente)
        font = QFont()
        ##font.setBold(True)
        font.setStyle(QFont.StyleItalic)
        action.setFont(font)
        menu.exec_(self.newTabButton.mapToGlobal(QPoint(0, self.newTabButton.height())))

    def activer_module(self, nom, selectionner=True):
        """Active le module `nom`.

        Retourne `True` si le module a bien été activé (ou est déjà actif),
        `False` sinon."""
        if nom not in param.modules_actifs:
            print("Warning: Le module %s n'a pas été trouvé." %repr(nom))
            return False
        elif param.modules_actifs[nom]:
            print('Le module %s est déjà activé.' %repr(nom))
        else:
            param.modules_actifs[nom] = True
            module = modules.importer_module(nom)
            if module is None:
                print("Warning: Impossible d'importer le module %s." %nom)
                return False
            panel = module._panel_(self, module)
            self.nouvel_onglet(panel)
            if selectionner:
                self.changer_onglet(panel)
        return True

    def nouvel_onglet(self, panel, i=None):
        "Ajouter un nouvel onglet à la position 'i'."
        if i is None:
            self._liste.append(panel)
            self.addTab(panel, panel.titre)
        else:
            self._liste.insert(i, panel)
            self.insertTab(i, panel, panel.titre)
        setattr(self, panel.module._nom_, panel)
        if self.count() > 1:
            self.closeTabButton.setEnabled(True)

    def deplacer_onglet(self, i, j):
        "Déplace l'onglet situé en position `i` à la position `j`."
        if i != j:
            self.tabBar.moveTab(i, j)

    def fermer_onglet(self, i=None):
        "Ferme l'onglet situé en position `i`."
        if self.count() > 1:
            if i is None:
                i = self.currentIndex()
            panel = self._liste.pop(i)
            delattr(self, panel.module._nom_)
            self.deleteTab(i)
            param.modules_actifs[panel.nom] = False
        if self.count() <= 1:
            self.closeTabButton.setEnabled(False)

    def deleteTab(self, i):
        """Supprime le ième onglet.

        Ne pas utiliser directement ; utiliser `fermer_onglet()` à la place."""
        tab = self.widget(i)
        self.removeTab(i)
        tab.close()
        tab.deleteLater()

    def evt_changer(self, index):
        """Actions effectuées lorsqu'on change d'onglet."""
        if self._ancien_onglet is not None:
            self._ancien_onglet.desactiver()
        if index != -1:
            onglet = self._liste[index]
            self.actualise_onglet(onglet)
            # Le module nouvellement sélectionné peut exécuter
            # des actions personnalisées à cette occasion.
            onglet.activer()
            self._ancien_onglet = onglet
        else:
            self._ancien_onglet = None


    def evt_deplacer_onglet(self, new_index, old_index):
        # Mise à jour de self._liste
        # XXX: self._liste est-il toujours utile depuis le passage à Qt ?
        self._liste.insert(new_index, self._liste.pop(old_index))


    def actualise_onglet(self, onglet):
        self.parent.setMenuBar(onglet.module._menu_(onglet)) # change le menu de la fenetre
        onglet.changer_titre() # change le titre de la fenetre


    def onglet(self, nom):
        "nom : nom ou numéro de l'onglet."
        if type(nom) == int:
            return self._liste[nom]
        return getattr(self, nom, None)


    @property
    def onglet_actuel(self):
        if self._liste:
            return self._liste[self.currentIndex()]

    def onglet_suivant(self, event):
        self.setCurrentIndex((self.currentIndex() + 1) % self.count())

    def __bool__(self):
        return bool(self._liste)

    def __iter__(self):
        return iter(self._liste)

    def changer_onglet(self, onglet):
        """Changer d'onglet actif.

        `onglet` : l'onglet proprement dit, ou son nom, ou son numéro."""
        if isinstance(onglet, str):
            onglet = self._liste.index(getattr(self, onglet.lower()))
        elif not isinstance(onglet, int):
            onglet = self._liste.index(onglet)
        self.setCurrentIndex(onglet)


    def actualiser_liste_onglets(self):
        # On commence par vérifier que la liste des modules à charger n'est pas vide
        modules_a_charger = [nom for nom, val in param.modules_actifs.items() if val]
        print("Modules à charger :", modules_a_charger)
        if not modules_a_charger:
            # On affiche l'onglet de bienvenue par défaut.
            modules_a_charger = ['bienvenue']

        # `pos` indique la progression du classement:
        # tous les onglets situés avant `pos` sont déjà classés.
        pos = 0
        for nom in modules_a_charger:
            try:
                module = modules.importer_module(nom)
                if module is not None:
                    for i, panel in enumerate(self._liste[pos:]):
                        if panel.module is module:
                            # Déplacer le panel en position pos
                            self.deplacer_onglet(pos + i, pos)
                            # Mettre à jour la position
                            pos += 1
                            break
                    else:
                        # Créer un onglet en position pos
                        self.nouvel_onglet(module._panel_(self, module), pos)
                        # Mettre à jour la position
                        pos += 1
            except Exception:
                param.modules_actifs[nom] = False
                print("\n** MODULE '%s' : ERREUR FATALE **\n" % nom)
                print_error()
                msg = ("Le programme va redémarrer sans le module '%s'." % nom)
                print('\n' + len(msg)*'-')
                print(msg)
                print("Veuillez patienter...")
                print(len(msg)*'-' + '\n')
                # Ne pas redémarrer pendant l'initialisation... (appeler la
                # méthode .close() à l'intérieur de la méthode .__init__()
                # ne fonctionne pas).
                param._restart = True

        # Supprimer tous les onglets qui sont situés après pos
        while pos < self.count():
            self.fermer_onglet(pos)


    # -------------------
    # Sauvegardes, export
    # -------------------

    filtres_save = ("Fichiers " + NOMPROG + " (*.geo);;"
                    "Fichiers " + NOMPROG + " compressés (*.geoz);;"
                    "Tous les fichiers (*.*)")

    filtre_session = "Session Géophar (*.geos)"

    def NewFile(self):
        self.onglet_actuel.creer_feuille()


    def SaveFile(self):
        if self.onglet_actuel.nom_sauvegarde:
            self.onglet_actuel.sauvegarder()
        else:
            # Pas de nom par défaut.
            self.SaveFileAs()


    def SaveFileAs(self):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille de travail courante
        if actuelle and actuelle.sauvegarde["nom"]:
            fichier = actuelle.sauvegarde["nom"] # le nom par defaut est le nom précédent
            dir = actuelle.sauvegarde["repertoire"]
        else:
            fichier = ""
            if param.rep_save is None:
                dir = param.repertoire
            else:
                dir = param.rep_save
        filtre = ("Fichiers %s compressés (*.geoz)" if param.compresser_geo else '')
        path, filtre = QFileDialog.getSaveFileNameAndFilter(self, "Enregistrer sous ...",
                                   os.path.join(dir, fichier), self.filtres_save, filtre)

        if path:
            # Sauvegarde le répertoire pour la prochaine fois
            param.rep_save = os.path.dirname(path)
            if param.rep_open is None:
                param.rep_open = param.rep_save
            if param.rep_export is None:
                param.rep_export = param.rep_save

            self.onglet_actuel.sauvegarder(path)


    def OpenFile(self, _event=None, detecter_module=True):
        # `_event=None` est un argument factice, qui est sert à consommer le booléen
        # renvoyé en argument lorsque OpenFile est lié au signal QAction.triggered.
        # Cf. doc Qt :
        # void QAction::triggered ( bool checked = false )   [signal]
        if param.rep_open is None:
            dir = param.repertoire
        else:
            dir = param.rep_open
        filtre = ("Fichiers %s compressés (*.geoz)" if param.compresser_geo else '')
        paths, filtre = QFileDialog.getOpenFileNamesAndFilter(self, "Choisissez un fichier", dir,
                                             self.filtres_save, filtre)
        if paths:
            # Sauvegarde le répertoire pour la prochaine fois
            param.rep_open = os.path.dirname(paths[0])
            if param.rep_save is None:
                param.rep_save = param.rep_open
            if param.rep_export is None:
                param.rep_export = param.rep_open

            for path in paths:
                if detecter_module: # on detecte dans quel onglet le fichier doit etre ouvert
                    self.ouvrir(path)
                else: # on l'ouvre dans l'onglet actuellement ouvert
                    self.onglet_actuel.ouvrir(path) # ouvre tous les fichiers selectionnes



    def OpenFileHere(self):
        """Ouvrir le fichier dans le module courant.

        Par défaut, sinon, le fichier est ouvert dans le module qui l'a crée."""
        self.OpenFile(detecter_module=False)


    def ouvrir(self, fichier, en_arriere_plan = False):
        """Ouvre un fichier dans l'onglet adéquat.

        'fichier' est soit l'adresse d'un fichier .geo, soit une instance de FichierGEO.
        """
        if not isinstance(fichier, FichierGEO):
            fichier, message = ouvrir_fichierGEO(fichier)
            self.parent.message(message)
        module = self.onglet(fichier.module)
        if module is None:
            if self.activer_module(fichier.module, selectionner=(not en_arriere_plan)):
                module = self.onglet(fichier.module)
            else:
                self.parent.message("Le module '%s' n'a pas été trouvé." % fichier.module)
                return
        if not en_arriere_plan:
            self.changer_onglet(module) # affiche cet onglet
        module.ouvrir(fichier) # charge le fichier dans le bon onglet


    def ExportFile(self, lieu = None, sauvegarde = False, exporter = True):
        """Le paramètre sauvegarde indique qu'il faut faire une sauvegarde simultanée.
        (attention, on ne vérifie pas que le fichier .geo n'existe pas !).
        """

        actuelle = self.onglet_actuel.feuille_actuelle # feuille de travail courante
        if actuelle and actuelle.sauvegarde["export"]:
            dir, fichier = os.path.split(actuelle.sauvegarde["export"]) # on exporte sous le même nom qu'avant par défaut
        elif actuelle and actuelle.sauvegarde["nom"]:
            fichier = actuelle.sauvegarde["nom"] # le nom par defaut est le nom de sauvegarde
            dir = actuelle.sauvegarde["repertoire"]
        else:
            fichier = ""
            if param.rep_export is None:
                dir = param.repertoire
            else:
                dir = param.rep_export


        lieu = lieu or self.onglet_actuel.nom # par defaut, le lieu est l'onglet courant

        description_formats = sorted(backend_bases.FigureCanvasBase.filetypes.items())
        formats_supportes = sorted(backend_bases.FigureCanvasBase.filetypes)


        def format(typ, description):
            return typ.upper() + ' - ' + description + ' (*.' + typ + ')'
        filtres = [format(k, v) for k, v in description_formats]

        format = ''
        if '.' in fichier and fichier[-1] != '.':
            # On récupère l'extension du nom de fichier
            format = fichier.rsplit('.', 1)[1]

        if format not in formats_supportes:
            format = param.format_par_defaut
            if format not in formats_supportes:
                print("Warning: format par defaut incorrect: " + repr(format))
                format = 'png'

        for filtre in filtres:
            if filtre.endswith(format + ')'):
                break

        path, filtre = QFileDialog.getSaveFileNameAndFilter(self, "Exporter l'image",
                                           os.path.join(dir, fichier), ';;'.join(filtres),
                                           filtre)

        if not path:
            return # Quitte sans sauvegarder.

        # Vérifie si le nom de fichier possède une extension
        for format in formats_supportes:
            if path.lower().endswith(format):
                break
        else:
            # Sinon, on en rajoute une.
            i = filtre.rindex('.')
            format = filtre[i + 1:-1]
            path += '.' + format

        # Sauvegarde le répertoire pour la prochaine fois
        param.rep_export = os.path.dirname(path)
        if param.rep_save is None:
            param.rep_save = param.rep_export
        if param.rep_open is None:
            param.rep_open = param.rep_export
        if sauvegarde:
            param.rep_save = param.rep_export
        # Sauvegarde le format pour la prochaine fois
        param.format_par_defaut = format
        ##print 'param.format_par_defaut', param.format_par_defaut

        try:
            if sauvegarde:
                geofile_name = path.rsplit('.', 1)[0] + ('.geoz' if param.compresser_geo else '.geo')
                self.onglet(lieu).sauvegarder(geofile_name)
            # Save Bitmap
            if exporter:
                self.onglet(lieu).exporter(path)
        except:
            print_error()
            self.parent.message("Erreur lors de l'export.")
        return path


    def ExportAndSaveFile(self, lieu=None):
        self.ExportFile(lieu=lieu, sauvegarde=True)

    def CloseFile(self):
        self.onglet_actuel.fermer_feuille()

    def NouvelleSession(self):
        reponse = QMessageBox.question(self, 'Ouvrir une session vierge ?',
                                       'Voulez-vous démarrer une nouvelle session ?\n'
                                       'Attention, la session actuelle sera perdue.',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.Yes)
        if reponse == QMessageBox.Yes:
            self.parent.gestion.reinitialiser_session()

    def SauverSession(self):
        filtre = self.filtre_session
        path = self._nom_fichier_session
        path, filtre = QFileDialog.getSaveFileNameAndFilter(self, "Sauver la session sous ...",
                                           path, filtre, filtre)
        if not path.endswith('.geos'):
            path += '.geos'
        if path:
            # Mémorise l'emplacement pour la prochaine fois
            self._nom_fichier_session = path
            # Enregistrement de la session
            self.parent.gestion.sauver_session(lieu=path, force=True)

    def ChargerSession(self):
        filtre = self.filtre_session
        path = self._nom_fichier_session
        path, filtre = QFileDialog.getOpenFileNameAndFilter(self,
                            "Choisissez un fichier de session",
                            path or path2(param.emplacements['session']),
                            filtre, filtre)
        if path:
            if not path.endswith('.geos'):
                path += '.geos'
            # Mémorise l'emplacement pour la prochaine fois
            self._nom_fichier_session = path
            # Charge la session
            self.parent.gestion.charger_session(lieu=path)

    def ChargerSessionPrecedente(self):
        reponse = QMessageBox.question(self, 'Recharger la session précédente ?',
                                       'Voulez-vous recharger la session précédente ?\n'
                                       'Attention, la session actuelle sera perdue.',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.Yes)
        if reponse == QMessageBox.Yes:
            self.parent.gestion.charger_session()

    # ----------
    # Impression
    # ----------

    ##def PageSetup(self):
        ##self.a_venir()

    def Printout(self):
        # Version utilisant QSvg
        # Fixme: l'alpha n'est pas bien rendu
        # (le fond des polygones est absent)
        # Le fond est bien présent après export avec matplotlib pourtant.
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        dialog.setOption(QPrintDialog.PrintPageRange, False)
        dialog.setOption(QPrintDialog.PrintToFile, True)
        dialog.setOption(QPrintDialog.PrintShowPageSize, True)
        dialog.setWindowTitle("Imprimer le document")
        if (dialog.exec_() == QDialog.Accepted):
            painter = QPainter(printer)
            try:
                output = StringIO()
                self.onglet_actuel.canvas.exporter(output, format='svg')
                svg = QSvgRenderer(QByteArray(output.getvalue()), self)
                size = svg.defaultSize()
                size.scale(painter.viewport().size(), Qt.KeepAspectRatio)
                rect = QRectF(0, 0, size.width(), size.height())
                svg.render(painter, rect)
            finally:
                painter.end()


    ##def Printout(self):
        ##printer = QPrinter(QPrinter.HighResolution)
        ##dialog = QPrintDialog(printer, self)
        ##dialog.setOption(QPrintDialog.PrintPageRange, False)
        ##dialog.setOption(QPrintDialog.PrintToFile, True)
        ##dialog.setOption(QPrintDialog.PrintShowPageSize, True)
        ##dialog.setWindowTitle("Imprimer le document")
        ##if (dialog.exec_() == QDialog.Accepted):
            ##painter = QPainter(printer)
            ##psize = printer.pageRect(QPrinter.Inch)
            ### QSizeF -> tuple
            ##tsize = float(psize.width())*2.54, float(psize.height())*2.54
            ##print printer.resolution(), tsize
            ##img = self.onglet_actuel.canvas.as_QImage(dpi=printer.resolution(),
                                                      ##taille=tsize,
                                                      ##keep_ratio=True)
            ##size = img.size()
            ##rect = painter.viewport()
            ##size.scale(rect.size(), Qt.KeepAspectRatio)
            ##painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            ##painter.setWindow(img.rect())
            ##painter.drawImage(0, 0, img)
            ##painter.end()

    def a_venir(self):
        QMessageBox.information(self, "A venir !", "Fonctionnalité non présente pour l'instant !")


    # ---------------------------------------------
    # Boîtes de dialogue liées à la feuille ouverte
    # ---------------------------------------------

    def supprimer(self):
        canvas = self.onglet_actuel.canvas
        dlg = SupprimerObjet(self)
        if dlg.exec_() == QDialog.Accepted:
            with canvas.geler_affichage(actualiser=True, sablier=True):
                for selection in dlg.selectedItems():
                    try:
                        # Il est normal que des erreurs soient renvoyées
                        # si un objet dépendant d'un autre est déjà supprimé.
                        objet = selection.text().split()[1]
                        canvas.feuille_actuelle.objets[objet].supprimer()
                    except Exception:
                        print_error()
                canvas.feuille_actuelle.interprete.commande_executee()


    def editer(self):
        feuille = self.onglet_actuel.feuille_actuelle
        if feuille:
            objets = []
            dlg = EditerObjet(self)
            if dlg.exec_() == QDialog.Accepted:
                objets = [feuille.objets[selection.text().split()[1]] for selection in dlg.selectedItems()]

            if objets:
                win = Proprietes(self, objets)
                win.show()


    def creer_objet(self, classe):
        canvas = self.onglet_actuel.canvas
        dl = classe(self)
        while dl.affiche() == QDialog.Accepted:
            try:
                canvas.executer(dl.commande(), parser = True)
                break
            except NameError:
                print_error()
                canvas.message('Erreur : nom déjà utilisé ou nom réservé.')
            except:
                print_error()
                canvas.message('Erreur : paramètres incorrects.')


    def Animer(self):
        d = DialogueAnimation(self)
        d.show()

    def Histo(self):
        contenu = self.onglet_actuel.feuille_actuelle.sauvegarder()
        h = FenCode(self, "Contenu interne de la feuille", contenu, self.executer_dans_feuille_courante)
        h.show()

    def executer_dans_feuille_courante(self, instructions):
        self.onglet_actuel.creer_feuille()
        self.onglet_actuel.feuille_actuelle.charger(instructions)

    def Proprietes(self):
        actuelle = self.onglet_actuel.feuille_actuelle # feuille courante
        ProprietesFeuille(self, actuelle).show()


    # -------------------------
    # Autres boîtes de dialogue
    # -------------------------

    def Options(self):
        fen_options = FenetreOptions(self, param_options)
        fen_options.options_modified.connect(self.apply_options)
        fen_options.show()

    def apply_options(self):
        self.actualiser_liste_onglets()
        for parametre in ('decimales', 'unite_angle', 'tolerance'):
            geolib.contexte[parametre] = getattr(param, parametre)

    def Aide(self):
        open_new_tab(path2("%/wxgeometrie/doc/html/help.html"))

    def Contacter(self):
        self.formulaire = Contact(self)
        self.formulaire.show()

    def About(self):
        dialog = About(self)
        dialog.exec_()

    def Informations(self):
        dialog = Informations(self)
        dialog.show()
