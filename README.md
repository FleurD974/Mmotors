Ce projet est réalisée dans le cadre de l'obtention d'un diplôme.
Afin d'avoir ce projet en local, il vous suffit de cloner ce repo et de suivre la suite.
Etant sous django afin de pouvoir avoir la base de donnée en locale, il vous suffit de configurer dans le fichier settings.py 
la variable DATABASES en suivant la documentation suivante : https://docs.djangoproject.com/fr/5.2/ref/databases/
Ensuite lancer votre serveur django avec la commande suivante: python manage.py runserver
Puis lancer les migrations à l'aide de la commande dans votre terminal: python manage.py makemigrations. 
puis python manage.py migrate
Rendez vous sur l'url indiqué après avoir lancé le serveur.
Créer un superuser grâce à la commande python manage.py createsuperuser vous permettera d'accèder aux fonctionnalités d'amin.
