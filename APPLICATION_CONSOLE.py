
import socket

hote, port = ('localhost', 2213)     # Même couple hote/port que celui du serveur
sock_client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # Création du socket UDP
address_serveur = ('localhost', 2212)     # Adresse du serveur

sock_client1.bind((hote, port))       # Liaison du socket à une adresse IP et un  port

#connexion au serveur
sock_client1.connect(address_serveur)
message = b"Bonjour le monde!"    # Message à envoyer

for i in range(5):
    print()
    sock_client1.send(message)     # Envoi du message
    print(f"Message envoyé : {message}")    # Affichage visuel du message envoyé
    print()
    print("***************** Message du serveur **********************")
    print()
    data, adresse = sock_client1.recvfrom(1024)    # Réception de la réponse
    print(data)     # Affichage visuel de la réponse
    print()

sock_client1.close()      # Fermeture du socket

