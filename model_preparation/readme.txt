Pré-requis :
	- Python 3.6 (minimum) installé ;


	- "model_preparation" :
		Ce dossier regroupe les implémentations effectuées pour traiter le modèle de deep learning 
		(dont la source est (https://keras.io/examples/vision/3D_image_classification/) et pour valider sa bonne utilisabilité.

Contenu et fonctionnalités :
	- Dossiers pour éléments de test :
		- "OKAPI" qui contient uniquement des images NIFTI de test
		- "DL_Models" qui contient les modèles DL entiers permettant de réaliser les étapes de préparation pour DF

	- "create_pbtxt_from_KerasH5.py" qui permet la création de fichier de configuration.pbtxt depuis un modèle 
	sauvé en .pb (et inversement) ;

	- "prepare_model.py" qui permet de créer un nouveau modèle depuis le modèle original, en .h5, en lui enlevant 
	des couches terminales (ici, 3 couches) et en enregistrant ce nouveau modèle en .pb ;

	- "process_NIFTI_input.py" qui est utilisé par "prepare_model.py" pour adapter les images NIFTI de test
	afin d'évaluer le bon fonctionnement les modèles (l'ancien et le nouveau) ;

Utilisations :
	- Le programme d'entrée est "prepare_model.py" et il réalise automatiquement avec les paramètrages de base (donc avec un modèle DL exemple) :

		-la reconstruction d'un modèle DL avec :

		    > soit la reconstruction d'un modèle Keras avec les poids HDF5 sauvegardés.
			> obligation ici (et dans tous les cas où le modèle sera customisé pour sa création) :
				- "def_model_module.py" qui reprèsente le module de création de l'architecture du modèle et permet de recréer
					la base du modèle customisé

			Rq : - méthode activée par défaut, ici.
			     - une autre voie de reconstruction d'un modèle HDF5 serait de sauvegarder la customisation du modèle et de la 
				réutiliser pour reconstruire le modèle)

		    > soit la reconstruction d'un modèle Keras savedmodel (dossier du modèle contenant : 
			1 dossier "keras_metadata.pb" + 1 dossier "saved_model.pb" ) :

			Rq : - solution de reconstruction plus simple pour les modèles Keras car toute la définission de l'architecture du
				modèle est contenu dans le moddèle (>> pas besoin de redéfinir un modèle customisé comme pour la méthode précédente)

		- l'affichage de l'architecture du modèle (permettant l'analyse des différentes couches de neurones artificiels)
		- la préparation d'une donnée d'entrée avec "process_NIFTI.py"
		- un test pour vérifier la bonne exécussion d'une inférence du modèle
		- une prédiciton et un affichage de la prédiction pour les couches de neurones (output) et (-4)
		- une modification du modèle DL initial par soustraction des 3 dernières couches de neurones artificiels
		- un affichage de la dernière couche neuronale du modèle obtenu et de la couche (-4) du modèle initial
		- un affichage de l'architecture du nouveau modèle obtenu (pour vérification)
		- une sauvegarde du modèle après modification en format ".pb" (utile pour Triton serveur) et ".h5" (utile pour le fichier de config ".pbtxt" pour Triton serveur).
		- la création du fichier de configuration "config.pbtxt" pour Triton serveur à l'aide du module "create_pbtxt_from_KerasH5.py"