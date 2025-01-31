Geophar
=======

*Le couteau suisse du prof de maths. :-)*

<http://wxgeo.free.fr/>

**License :** GNU Public License version 2 or higher

**Auteur :** Nicolas Pourcelot <wxgeo@users.sourceforge.net> (2005-2010)


La librairie *Sympy* ci-incluse est distribuée sous license BSD,
par la Sympy Development Team:

SymPy Development Team (2010). SymPy: Python library for symbolic mathematics
URL <http://www.sympy.org>.


Le module *decorator* est écrit et distribué par Michele Simionato (c) 2005.
URL <http://pypi.python.org/pypi/decorator>.



0. Téléchargement
-----------------

La dernière version officiellement publiée se trouve sur :

<http://sourceforge.net/projects/wxgeometrie/>


Pour télécharger la version en cours de développement :

`$ git clone git://github.com/wxgeo/wxgeometrie.git`

Derrière un firewall, vous pouvez également utiliser :
`$ git clone http://github.com/wxgeo/wxgeometrie.git`
(beaucoup plus lent !!)




1. Documentation
----------------

Pour l'installation, consultez le fichier *INSTALL*.

Le manuel de l'utilisateur est disponible à l'adresse suivante :

<http://wxgeo.free.fr/doc/html/help.html>

Vous pouvez également consulter ou compléter le wiki à cette adresse :

<http://www.maths.ac-aix-marseille.fr/webphp/wiki/index.php/Accueil#Aide_WxG.C3.A9om.C3.A9trie>



2. Tests
--------

Si vous envisager d'apporter une modification à Géophar, commencez par vérifier
que tous les tests de régression passent toujours.

Placez vous dans le répertoire de Géophar, et lancez la suite de tests :

    $ python3 -m unittest discover -v




3. Bref historique
------------------

En 2005, souhaitant apprendre la programmation orientée objet, je suis tombé
sur un article d'un développeur vantant Python.

Les logiciels de géométrie dynamique répandus étaient alors essentiellement
propriétaires (hasard du sort, six mois plus tard, la situation avait déjà bien
changé).

Après quelques essais de programmation en Python fin décembre 2004, je décidai
d'écrire un prototype de logiciel de géométrie dynamique, m'inspirant de Cabri
et Geoplan.

De fil en aiguille, WxGéométrie a acquis successivement toute une panoplie d'outils
au fur et à mesure de mes besoins d'enseignant : traceur de courbes, calculatrice,
statistiques, arbre de probabilités, tableaux LaTeX...



4. Remerciements
----------------

Un grand merci à tous ceux qui ont pris la peine de rapporter des bugs, faire des
commentaires, suggestions, etc.
Remerciements tous particuliers à Boris Mauricette, Jean-Pierre Garcia, Christophe Gragnic
et Georges Khaznadar pour leur contribution, ainsi qu'à Christophe Vrignaud, Christophe Bal, 
Stéphane Clément et Dominique Pommier pour leurs suggestions et encouragements.

Mes remerciements vont également à la Sympy Development Team,
et aux auteurs de Matplotlib, tant pour la qualité de leurs librairies que pour
leur disponibilité.
