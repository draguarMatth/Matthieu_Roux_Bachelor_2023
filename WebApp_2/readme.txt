Pré-requis :
	- Python 3.6 (minimum) installé ;

	- 1 serveur d'inférence Triton NVidia installé et en service sur le localhost port 8000 (s'il est installé diffèremment
	il faudra appliquer les bonnes options (voir les options dans quantImage.py) (voir "Installation du serveur Triton NVidia.txt") ;

	- Flask et autres librairies des fichiers .py installés ;

	- Triton client (paquet pip) (voir "Installation du client Triton NVidia.txt")

	- Navigateur Firefox (n'a pas été évalué sur d'autres navigateurs);


Fonctionnalités :
	
	Application finale réalisée durant ce travail de bachelor.
	Cette application est totalement fonctionnelle moyennant un compte d'accès quantImage-V2 avec des albums à disposition.

	Rq : 	- contacter le Pr Depeursinge Adrien, HES-SO Valais-Wallis - Haute Ecole de Gestion
		- S'il n'y a pas d'album disponible, un 'examen dicom test est à disposition dans DICOM_TEST mais la 
	connexion sécurisée reste obligatoire.

	L'application a été testée et validée avec un serveur d'inférence Triton installé en localhost.

	Elle permet de :
		- se connecter à la zone sécurisée QuantImage-V2 permettant l'accès à des albums d'examens médicaux anonymisés via Kheops ;

		- choisir un album d'images médicales CT, PT et/ou IRM ;

		- choisir une collection d'images de cet album ;

		- choisir un modèle d'analyse à disposition sur le serveur Triton installé pour son inférence ;

		- visualiser et télécharger les résultats sous forme d'un fichier .zip

		- Rq : tous les fichiers temporaires téléchargés par l'application sont stockés dans "static/downloads" 
		et se vident automatiquement au cours des utilisations itérées.


Utilisaton de l'application :

	- Télécharger le répertoire GitHub ( https://github.com/draguarMatth/Matthieu_Roux_Bachelor_2023.git ) ;

	- En ligne de commande :
		- ce rendre dans le répertoire WebApp_2 (cd .../WebApp_2)

		- exécuter la commande : python3 app.py
