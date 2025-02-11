
import socket

# Création du socket UDP

hote, port = ('localhost', 2212)     # address serveur
address_client = ('localhost', 2213)     # address client

sock_servr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # Création du socket de type SOCK_DGRAM pour UDP
sock_servr.bind((hote, port))
print("Le serveur est démarré sur le port {}".format(port))

# Boucle infinie pour recevoir les messages des clients
message_confirmation = b"Message bien recu"

while True:
    print("*"*40)
    print("Le serveur est en écoute sur le port {}".format(port))      # Affichage visuel de l'état du serveur
    data, adresse = sock_servr.recvfrom(1024)                           # Réception des données
    print("Message reçu : {} de la part de {}".format(data, adresse))     # Affichage visuel des données reçues
    sock_servr.sendto(message_confirmation,address_client)                      # Réponse au client
    print("Message de confirmation envoyé")                    # Affichage visuel de l'état du serveur
    print()

print("Fermeture de la connexion")            # Affichage visuel de l'état du serveur
sock_servr.close()      # Fermeture du socket
print("Fermeture du socket")                  # Affichage visuel de l'état du serveur


