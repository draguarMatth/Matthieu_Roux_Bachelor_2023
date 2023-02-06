Pré-requis :
	- Python 3.6 (minimum) installé ;


	- "model_preparation" :
		Ce dossier regroupe les implémentations effectuées pour traiter le modèle de deep learning 
		(dont la source est (https://keras.io/examples/vision/3D_image_classification/) et pour valider sa bonne utilisabilité.

Contenu et fonctionnalités :
	- "OKAPI" qui contient uniquement des images NIFTI de test

	- "create_pbtxt_from_KerasH5.py" qui permet la création de fichier de configuration.pbtxt depuis un modèle 
	sauvé en .pb (et inversement) ;

	- "features_names" utile uniquement pour mettre en lien les résultats avec un fichier de référence textuel 
	(utile pour de la classification, par exemple) ;

	- "prepare_model.py" qui permet de créer un nouveau modèle depuis le modèle original, en .h5, en lui enlevant 
	des couches terminales (ici, 3 couches) et en enregistrant ce nouveau modèle en .pb ;

	- "process_NIFTI_input.py" qui est utilisé par "prepare_model.py" pour adapter les images NIFTI de test
	afin d'évaluer le bon fonctionnement les modèles (l'ancien et le nouveau) ;

