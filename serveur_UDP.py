
import socket

# Création du socket UDP

hote, port = ('localhost', 2212)     # couple hote/port sous forme de tuple

socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # Création du socket de type SOCK_DGRAM pour UDP
socket_UDP.bind((hote, port))
print("Le serveur est démarré sur le port {}".format(port))

# Boucle infinie pour écouter les connexions
while True:
    #socket_UDP.listen()                                              # Le serveur écoute sur le port 2212 et est en attente de connexion
    print("Le serveur est en écoute sur le port {}".format(port))      # Affichage visuel de l'état du serveur
data, adresse = socket_UDP.recvfrom(1024)
print("APPLICATION_CONSOLE est connecté au serveur")          # Affichage visuel de l'état du serveur


connexion.close()   # Fermeture de la connexion
print("Fermeture de la connexion")            # Affichage visuel de l'état du serveur
socket_UDP.close()      # Fermeture du socket
print("Fermeture du socket")                  # Affichage visuel de l'état du serveur


