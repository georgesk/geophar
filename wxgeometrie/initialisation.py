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

import sys, time, os, optparse, itertools, traceback, imp
from os.path import dirname, realpath

t0 = time.time()

from . import param
# Attention, les param�tres import�s explicitement ici dans l'espace des noms
# du module `initialisation` ne pourront pas �tre modifi� en ligne de commande :
# en effet, pour modifier les param�tres via la ligne de commande,
# on met � jour l'espace des noms du module param.
# En particulier, il ne faut *PAS* �crire ``from .param import debug``,
# car alors, ``$ geophar -b`` ne prendrait pas en compte le ``-b``
# lors de l'initialisation.
from .param import dependances, NOMPROG, NOMPROG2, LOGO, plateforme, GUIlib

nomprog = NOMPROG2.lower()

if param.py2exe:
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
            print(u'** Erreur fatale ** : le module %s doit �tre install� !' %module)
            if plateforme == 'Linux':
                print("Sous Ubuntu/Debian, tapez 'sudo apt-get install %s' pour \
                       installer le module manquant." %dependances[module])
            sys.exit(-1)


def gerer_arguments():
    u"""On r�cup�re les options �ventuelles pass�es au programme.

    -a ou --all : essaie de d�tecter tous les modules possibles pour les int�grer au d�marrage
    ex: python wxgeometrie.pyw --all monfichier1.geo monfichier2.geo

    -p ou --param ou --parametres : modifier le contenu du module 'param'. Les parametres sont s�par�s par des points-virgules.
    ex: python wxgeometrie.pyw --param version='0.1';tolerance=0.01 monfichier1.geo monfichier2.geo

    -d ou --defaut : ne pas charger les pr�f�rences"""

    parametres_additionnels = {}

    parser = optparse.OptionParser(prog = NOMPROG2, usage = "usage: %prog [options] [fichiers...]",
                                   version = "%prog " + param.version,
                                   description = NOMPROG2 + """ est un logiciel de mathematiques de niveau lycee.
                                                    Il permet notamment de faire de la geometrie dynamique et du calcul formel.""")
    parser.add_option("-a", "--all", action = "store_true", help="detecter tous les modules presents et les integrer au demarrage")
    parser.add_option("-m", "--modules", help="specifier les modules a charger. ex: %s -m traceur,calculatrice" %nomprog)
    parser.add_option("-d", "--defaut", action = "store_true", help="utiliser les parametres par defaut, sans tenir compte des preferences")
    parser.add_option("-n", "--nouveau", action = "store_true", help="ouvrir une nouvelle session vierge")
    parser.add_option("-b", "--debug", action = "store_true", help="afficher les eventuels messages d'erreurs lors de l'execution")
    parser.add_option("--nodebug", action = "store_true", help="ne pas afficher les messages d'erreurs lors de l'execution")
    parser.add_option("-w", "--warning", action = "store_true", help="afficher les eventuels avertissements lors de l'execution")
    parser.add_option("--nowarning", action = "store_true", help="ne pas afficher les avertissements lors de l'execution")
    parser.add_option("-p", "--parametres", help="modifier les parametres. ex: %s -p 'tolerance=0.001;version=\"1.0\"'" %nomprog)
    parser.add_option("-r", "--recompile", action = "store_true", help="supprimer recursivement tous les fichiers .pyc, pour obliger python a recompiler tous les fichiers sources au demarrage.")
    parser.add_option("-s", "--script", action = "store_true", help="passer en mode script (ie. sans interface graphique). Ex: %s -s -i mon_script.txt -o mon_image.png" %nomprog)
    parser.add_option("-i", "--input", help="(mode script) fichier contenant le script de construction de figure, ou fichier .geo.")
    parser.add_option("-o", "--output", help="(mode script) fichier image. L'extension determine le type de fichier.")

# parser.set_defaults()

    (options, args) = parser.parse_args()

    if options.defaut:
        param.charger_preferences = False

    if options.modules:
        # Les s�parateurs accept�s entre les noms de modules sont , et ;
        if ',' in options.modules:
            a_activer = options.modules.split(',')
        else:
            a_activer = options.modules.split(';')
        parametres_additionnels["modules_actifs"] = dict((module, (module in a_activer)) for module in param.modules)

    if options.all:
        parametres_additionnels["modules_actifs"] = dict.fromkeys(param.modules, True)


    if options.debug:
        parametres_additionnels["debug"] = True

    if options.nodebug:
        parametres_additionnels["debug"] = False

    if options.warning:
        parametres_additionnels["warning"] = True

    if options.nowarning:
        parametres_additionnels["warning"] = False

    if options.parametres:
        for parametre in options.parametres.split(";"):
            try:
                nom, valeur = parametre.split("=", 1)
                parametres_additionnels[nom] = eval(valeur) # pas sensass question s�curit�... :-( (?)
            except Exception:
                #raise
                print "Erreur: Parametre incorrect :", parametre
                print sys.exc_info()[0].__name__, ": ", sys.exc_info()[1]

    if options.recompile:
        for root, dirs, files in os.walk(os.getcwdu()):
            for file in files:
                if file.endswith(".pyc"):
                    os.remove(os.path.join(root,file))

    if (options.input or options.output) and not options.script:
        print("Warning: options --input et --output incorrectes en dehors du mode script.\n"
              "Exemple d'utilisation correcte : %s -s -i mon_script.txt -o mon_image.png." %nomprog)

    arguments = []

    # Sous les Unix-like, les espaces dans les noms de fichiers sont mal g�r�s par python semble-t-il.
    # Par exemple, "mon fichier.geo" est coup� en "mon" et "fichier.geo"
    complet = True
    for arg in args:
        if complet:
            arguments.append(arg)
        else:
            arguments[-1] += " " + arg
        complet = arg.endswith(".geo") or arg.endswith(".geoz")

    for nom in parametres_additionnels:
        if not hasattr(param, nom):
            print(u"Attention: Param�tre inconnu : " + nom)

    return parametres_additionnels, arguments, options



def universal_unicode(chaine):
    if not isinstance(chaine, basestring):
        chaine = str(chaine)
    if not isinstance(chaine, unicode):
        try:
            chaine = chaine.decode(param.encodage)
        except UnicodeError:
            try:
                chaine = chaine.decode('utf8')
            except UnicodeError:
                chaine = chaine.decode('iso-8859-1')
    return chaine

uu = universal_unicode


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

# Emplacement du module python nomm� wxgeometrie
param.EMPLACEMENT = dirname(realpath(sys._getframe().f_code.co_filename))


def path2(chemin):
    u"""Transforme le chemin en rempla�ant les / et \\ selon le s�parateur utilis� par le syst�me.

    % est remplac� par l'emplacement du programme (contenu dans param.EMPLACEMENT).
    Exemple : path2("%/images/archives/old.png").
    ~ fait r�f�rence au r�pertoire personnel de l'utilisateur (ex: /home/SteveB/ sous Linux.
    """
    return os.path.normpath(os.path.expanduser(uu(chemin).replace("%", uu(param.EMPLACEMENT))))


# S'assurer que les dossiers log/, session/, etc. existent:
for emplacement in param.emplacements.values():
    emplacement = path2(emplacement)
    try:
        if not os.path.isdir(emplacement):
            os.makedirs(emplacement)
            print(u'Cr�ation du r�pertoire : ' + emplacement)
    except IOError:
        print(u"Impossible de cr�er le r�pertoire %s !" %emplacement)


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
    # � faire avant d'importer API et LIB
    parametres_additionnels, arguments, options = gerer_arguments()

    if param.verbose:
        print u'Arguments de la ligne de commande :', parametres_additionnels, arguments
        if options.script:
            print u"--- Mode script activ�. ---"

    if param.py2exe:
        print sys.path
        sys.path.extend(('library.zip\\matplotlib', 'library.zip\\' + GUIlib))

##    #Test des imports
##    from . import GUI
##    import wx # apr�s GUI (wxversion.select() must be called before wxPython is imported)

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
        # R�cup�ration d'un crash �ventuel
        path_lock = path2(param.emplacements['session'] + "/lock")
        crash = os.path.isfile(path_lock)

        try:
            open(path_lock, 'w').close()
            param.ecriture_possible = True
        except IOError:
            print(u"Warning: impossible de cr�er le fichier '%s'." %path_lock)
            param.ecriture_possible = False

        # Mise � jour des param�tres en fonction des pr�f�rences de l'utilisateur
        # (NB: � faire avant d'importer modules.py, qui lui-m�me utilise param.modules_actifs)
        path = path2(param.emplacements['preferences'] + "/parametres.xml")
        try:
            if os.path.exists(path):
                if param.charger_preferences:
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
                else:
                    actualiser_module(param, None)
        except:
            sys.excepthook(*sys.exc_info())

        param.__dict__.update(parametres_additionnels)

        if options.script:
            from .GUI.mode_script import mode_script
            msg = mode_script(options.input, options.output)
            if msg:
                print msg

        else:
            from .GUI.app import app, splash
            app.nom(NOMPROG)
            splash_screen = splash(path2(LOGO))

            from .GUI.fenetre_principale import FenetrePrincipale
            if param.debug:
                print("Temps d'initialisation: %f s" % (time.time() - t0))
            frame = FenetrePrincipale(app, fichier_log = fichier_log)
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
            elif (param.sauver_session or crash) and not options.nouveau:
                try:
                    if crash:
                        print(NOMPROG + u" n'a pas �t� ferm� correctement.\n"
                              "Tentative de restauration de la session en cours...")
                    frame.gestion.charger_session()
                except:
                    print(u"Warning: La session n'a pas pu �tre restaur�e.")
                    print_error()
            frame.show()
            if param.debug:
                print('Temps de d�marrage: %f s' % (time.time() - t0))
            app.boucle()
            sorties.close()
        os.remove(path_lock)

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
    sorties.close()
    sys.exit("Erreur fatale lors de l'initialisation.")
