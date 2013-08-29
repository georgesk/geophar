# -*- coding: iso-8859-1 -*-
from __future__ import division # 1/2 == .5 (par defaut, 1/2 == 0)

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

import time
t0 = time.time()
import sys, os, itertools, traceback, imp, subprocess
from os.path import dirname, realpath, normpath

# Emplacement du module python nomm� wxgeometrie
EMPLACEMENT = dirname(dirname(realpath(sys._getframe().f_code.co_filename)))

if getattr(sys, '_launch_geophar', False):
    from .arguments import lire_arguments, traiter_arguments

    options, arguments = lire_arguments()


    # Le splash screen doit �tre affich� le plus t�t possible.
    # Par contre, il ne doit pas �tre affich� si le fichier est import� simplement
    # comme module.
    if not (options.script or options.lister_modules):
        from .GUI.app import app, splash

        splash_screen = splash(normpath(EMPLACEMENT + '/wxgeometrie/images/logo6-1.png'))
        # .showMessage() doit �tre appel� pour que le splash screen apparaisse.
        # cf. https://bugreports.qt-project.org/browse/QTBUG-24910
        splash_screen.showMessage(u'Chargement en cours...')
        print(u"D�marrage GUI...")

    parametres_additionnels, arguments, options = traiter_arguments(options, arguments)

    from . import param
    # Attention, les param�tres import�s explicitement ici dans l'espace des noms
    # du module `initialisation` ne pourront pas �tre modifi� en ligne de commande :
    # en effet, pour modifier les param�tres via la ligne de commande,
    # on met � jour l'espace des noms du module param.
    # En particulier, il ne faut *PAS* �crire ``from .param import debug``,
    # car alors, ``$ geophar -b`` ne prendrait pas en compte le ``-b``
    # lors de l'initialisation.
    from .param import dependances, NOMPROG, NOMPROG2, LOGO, plateforme, GUIlib
    from .pylib.fonctions import path2, uu, str3

    param.EMPLACEMENT = EMPLACEMENT
    # Un identifiant unique pour chaque instance de wxgeometrie lanc�e.
    # Doit permettre notamment de g�rer les acc�s simultann�s aux ressources
    # (sauvegardes automatiques).
    # Chaque session est sauv�e automatiquement sous le nom :
    # 'config/session/session-%s.geos' % ID
    # Les ID successifs sont strictement incr�mentaux, ce qui fait qu'en cas de crash
    # il est facile de retrouver le dernier fichier de session (pour le recharger),
    # c'est celui qui a l'ID le plus �lev�.
    param.ID = ID = repr(t0).replace('.','-')

    if not options.script:
        app.nom(NOMPROG)
        if param.style_Qt:
            app.setStyle(param.style_Qt)
        app.icone(u"%/wxgeometrie/images/icone.ico")

    if param.py2exe:
        # Ce qui suit concerne seulement py2exe, et non py2app.
        if param.plateforme != 'Darwin':
            # cf. py2exe/boot_common.py
            # Par d�faut dans py2exe, sys.stdout redirige nul part,
            # et sys.stderr redirige vers un fichier .log via un m�canisme assez �labor�
            sys._py2exe_stderr = sys.stderr
            sys._py2exe_stdout = sys.stdout
            def msgbox(titre='Message', texte='', MB=sys._py2exe_stderr.write.func_defaults[0]):
                MB(0, texte.encode(param.encodage), titre.encode(param.encodage))
            # Outil de d�bogage avec py2exe
            def _test(condition = True):
                msgbox('** Test **', ('Success !' if condition else 'Failure.'))
    else:
        # Ne pas faire ces tests avec py2exe (non seulement inutiles, mais en plus ils �chouent).
        # Make sure I have the right Python version.
        if sys.version_info[:2] < param.python_min:
            print(u" ** Erreur fatale **")
            print(NOMPROG + u" n�cessite Python %d.%d au minimum.")
            print(u"Python %d.%d d�tect�." % (param.python_min + sys.version_info[:2]))
            sys.exit(-1)

        # Test for dependencies:
        for module in dependances:
            try:
                imp.find_module(module)
            except ImportError:
                msg = u'** Erreur fatale **\nLe module %s est introuvable !\n' % module

                if plateforme == 'Linux':
                    def which(cmd):
                        out = subprocess.Popen(("which", cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
                        sortie = out.read()
                        out.close()
                        return sortie

                    if which('apt-get'):
                        paquet = dependances[module]
                        if which('gksudo'):
                            msg += "\nVoulez-vous installer le paquet '%s' correspondant ?" % paquet
                        else:
                            msg += "Sous Ubuntu/Debian, tapez 'sudo apt-get install %s'" \
                                " pour installer le module manquant.\n" % paquet
                    print(msg)

                    if which('xmessage'):
                        btn = subprocess.call(["xmessage", "-buttons", "OK,Annuler",
                                  "-center", "-default", "OK", "-print", str3(msg)])
                        if btn == 101 and which('gksudo'):
                            # Installation du paquet manquant
                            if not subprocess.call(['gksudo', 'apt-get', 'install', paquet]):
                                continue
                else:
                    print(msg)
                sys.exit(-1)



    #def my_excepthook(exc_type, exc_obj, exc_tb):
    #    u"""Affiche l'erreur sans interrompre le programme.
    #    C'est un alias de sys.excepthook, mais qui est plus souple avec les encodages.
    #    """
    #    tb = traceback.extract_tb(exc_tb)
    #    print 'Traceback (most recent call last !)'
    #    for fichier, ligne, fonction, code in tb:
    #        print '    File "' + uu(fichier) +'", line ' + unicode(ligne) + ', in ' + uu(fonction)
    #        if code is not None:
    #            print '        ' + uu(code)
    #    print uu(exc_type.__name__) + ": " + uu(exc_obj)


    #sys.excepthook = my_excepthook

    class SortieTemporaire(list):
        def write(self, chaine):
            self.append(uu(chaine).encode(param.encodage))


    class SortiesMultiples(object):
        softspace = 0
        def __init__(self, obligatoires = (), facultatives = ()):
            self.obligatoires = list(obligatoires)
            self.facultatives = list(facultatives)
            self.total = 0

        def write(self, chaine):
            uni = uu(chaine)
            chaine = uni.encode(param.encodage)
    #        default_out = (sys.__stdout__ if not param.py2exe else sys.py2exe_stderr)
            # Sous Windows, l'encodage se fait en cp1252, sauf dans console o� cp850 est utilis� !
    #        default_out.write(chaine if plateforme != 'Windows' else uni.encode('cp850'))
            # Sous Windows, l'encodage se fait en cp1252, sauf dans console o� cp850 est utilis� !
            if not param.py2exe:
                sys.__stdout__.write(chaine if plateforme != 'Windows' else uni.encode('cp850'))

            self.total += len(chaine)
            if self.total - len(chaine) < param.taille_max_log <= self.total:
                chaine = u"Sortie satur�e !".encode(param.encodage)
            for sortie in self.obligatoires:
                sortie.write(chaine)
            if param.debug:
                for sortie in self.facultatives:
                    sortie.write(chaine)

        def flush(self):
            for sortie in itertools.chain(self.obligatoires, self.facultatives):
                if hasattr(sortie, 'flush'):
                    sortie.flush()

        def __del__(self):
            self.close()

        def close(self):
            for sortie in self.obligatoires:
                if hasattr(sortie, 'close'):
                    sortie.close()
            for sortie in self.facultatives:
                if hasattr(sortie, 'close'):
                    sortie.close()


    # S'assurer que les dossiers log/, session/, etc. existent:
    for emplacement in param.emplacements.values():
        emplacement = path2(emplacement)
        try:
            if not os.path.isdir(emplacement):
                os.makedirs(emplacement)
                print(u'Cr�ation du r�pertoire : ' + emplacement)
        except IOError:
            print(u"Impossible de cr�er le r�pertoire %s !" %emplacement)
            print_error()
        except Exception:
            print(u'Erreur inattendue lors de la cr�ation du r�pertoire %s.' %emplacement)
            print_error()


    # PARTIE CRITIQUE (redirection des messages d'erreur)
    # Attention avant de modifier, c'est tr�s difficile � d�boguer ensuite (et pour cause !)
    # R�duire la taille de cette partie au minimum possible.

    try:
        sorties = sys.stdout = sys.stderr = SortiesMultiples()
        # Tester sys.stdout/stderr (les plantages de sys.stderr sont tr�s p�nibles � tracer !)
        sorties.write('')
    except:
        if param.py2exe:
            sys.stderr = sys._py2exe_stderr
            sys.stdout = sys._py2exe_stdout
        else:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        raise

    log_filename = path2(param.emplacements['log'] + u"/messages.log")
    if param.enregistrer_messages and isinstance(sys.stdout, SortiesMultiples):
        try:
            sys.stdout.facultatives.append(SortieTemporaire())
            fichier_log = open(log_filename, 'w')
            fichier_log.write(NOMPROG.encode(param.encodage) + " version " + param.version + '\n')
            fichier_log.write(time.strftime("%d/%m/%Y - %H:%M:%S") + '\n')
            sys.stdout.obligatoires.append(fichier_log)
        except IOError:
            fichier_log = None
            param.enregistrer_messages = param.historique_log = False
            if param.py2exe:
                sys.stderr = sys._py2exe_stderr
                sys.stdout = sys._py2exe_stdout
            else:
                print(traceback.format_exc(sys.exc_info()))
                print('Warning: This exception was not raised.')
    else:
        fichier_log = None

    # FIN DE PARTIE CRITIQUE


    # On encl�t tout dans un try/except.
    # En effet, le sys.stderr personnalis� se comporte mal en cas d'erreur non intercept�e
    # (il semble qu'une partie de l'espace des noms ne soit d�j� plus accessible au moment o� l'erreur
    # est trait�e...??)
    try:
        # � faire avant d'importer API
        if param.verbose:
            print u'Arguments de la ligne de commande :', parametres_additionnels, arguments
            if options.script:
                print u"--- Mode script activ�. ---"

        if param.py2exe:
            print sys.path
            sys.path.extend(('library.zip\\matplotlib', 'library.zip\\' + GUIlib))

        if param.charger_psyco is not False:
            try:
                import psyco
                if param.charger_psyco is True:
                    psyco.full()
                else:
                    psyco.profile()
            except ImportError:
                pass



        def initialiser():
            from .API.parametres import actualiser_module
            from .pylib import print_error
            from .geolib import contexte
            # R�cup�ration d'un crash �ventuel
            path_lock = path2(param.emplacements['session'] + "/lock")
            crash = os.path.isfile(path_lock)

            try:
                open(path_lock, 'w').close()
                param.ecriture_possible = True
            except IOError:
                print(u"Warning: impossible de cr�er le fichier '%s'." %path_lock)
                param.ecriture_possible = False

            # On sauvegarde la valeur des param�tres par d�faut.
            copie = param.__dict__.copy()
            copie.pop("__builtins__", None)
            setattr(param, "_parametres_par_defaut", copie)

            # Mise � jour des param�tres en fonction des pr�f�rences de l'utilisateur.
            # (NB: � faire avant d'importer modules.py, qui lui-m�me utilise param.modules_actifs)
            path = path2(param.emplacements['preferences'] + "/parametres.xml")
            try:
                if os.path.exists(path) and param.charger_preferences:
                    if param.verbose:
                        print(u"Chargement des pr�f�rences...")
                    # On charge les pr�f�rences de l'utilisateur depuis parametres.xml.
                    a_verifier = dict((dicname, getattr(param, dicname)) for dicname in param.a_mettre_a_jour)
                    actualiser_module(param, path)
                    # Certains param�tres peuvent avoir besoin d'une mise � jour
                    # (en cas de changement de version du programme par exemple).
                    # Cela concerne en particulier les dictionnaires, qui peuvent gagner de nouvelles cl�s.
                    for dicname in param.a_mettre_a_jour:
                        for key, val in a_verifier[dicname].iteritems():
                            getattr(param, dicname).setdefault(key, val)
                    # Mise � jour du contexte de geolib:
                    for parametre in ('decimales', 'unite_angle', 'tolerance'):
                        contexte[parametre] = getattr(param,  parametre)
            except:
                sys.excepthook(*sys.exc_info())

            param.__dict__.update(parametres_additionnels)

            if options.script:
                from .GUI.mode_script import mode_script
                msg = mode_script(options.input, options.output)
                if msg:
                    print msg

            else:
                # param._restart est mis � True si l'application doit �tre red�marr�e.
                param._restart = False

                from .GUI.fenetre_principale import FenetrePrincipale
                if param.debug:
                    print("Temps d'initialisation: %f s" % (time.time() - t0))
                frame = FenetrePrincipale(app, fichier_log = fichier_log)
                if not param._restart:
                    splash_screen.finish(frame)
                    if isinstance(sys.stdout, SortiesMultiples):
                        if param.debug:
                            for msg in sys.stdout.facultatives[0]:
                                frame.fenetre_sortie.write(msg)
                        sys.stdout.facultatives[0] = frame.fenetre_sortie
                    if arguments:
                        try:
                            for arg in arguments:
                                frame.onglets.ouvrir(arg) # ouvre le fichier pass� en param�tre
                        except:
                            print_error() # affiche l'erreur intercept�e, � titre informatif
                            print(arg)
                    elif options.restaurer or ((param.auto_restaurer_session or crash)
                                                and not options.nouveau):
                        # On recharge la session pr�c�dente.
                        # (options.restaurer est utilis� quand on red�marre l'application)
                        try:
                            if crash:
                                print(NOMPROG + u" n'a pas �t� ferm� correctement.\n"
                                      "Tentative de restauration de la session en cours...")
                            # En g�n�ral, ne pas activer automatiquement tous les modules
                            # de la session pr�c�dente, mais seulement ceux demand�s.
                            frame.gestion.charger_session(activer_modules=crash)
                        except:
                            print(u"Warning: La session n'a pas pu �tre restaur�e.")
                            print_error()
                    frame.show()
                    if param.debug:
                        print('Temps de d�marrage: %f s' % (time.time() - t0))
                    app.boucle()
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                sorties.close()
            try:
                os.remove(path_lock)
            except OSError:
                print("Warning: impossible de supprimer %s." % repr(path_lock))
            if param._restart:
                args = [sys.executable, sys.argv[0], '--restaurer']
                # Nota: execv() a une syntaxe �trange : le nom de la commande lanc�e
                # (ie. sys.executable) doit r�appara�tre au d�but de la liste des arguments.
                print(u"\n=======================")
                print(u"Red�marrage en cours...")
                print(' '.join(args))
                print(u"=======================\n")
                os.execv(sys.executable, args)

    except Exception: # do *NOT* catch SystemExit ! ("wxgeometrie -h" use it)
        if param.py2exe:
            details = u"D�tails de l'erreur :\n"
            # 25 lignes maxi dans la fenetre
            l = uu(traceback.format_exc(sys.exc_info())).split('\n')[-25:]
            details += '\n'.join(l) + '\n\n'
            if param.enregistrer_messages:
                details += u"Pour plus de d�tails, voir \n'%s'." %log_filename
            else:
                details += u"Par ailleurs, impossible de g�n�rer le fichier\n'%s'." %log_filename
            msgbox(u"Erreur fatale lors de l'initialisation.", details)
        sys.excepthook(*sys.exc_info())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sorties.close()
        sys.exit("Erreur fatale lors de l'initialisation.")
