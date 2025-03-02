
import socket


# Fonction pour le processus de poignée de main
def ProcessusPoigneDeMain(socket):
    print("***************** Processus de poignée de main coté serveur **********************")
    print()
    print("***************** Reception du SYN **********************")
    print()
    data, adresse = socket.recvfrom(1024)   # Reception du SYN
    if data == b"SYN":
        print("SYN reçu")
    else:
        print("SYN non reçu")
    print()
    print("***************** Envoi du SYN-ACK **********************")
    print()
    socket.sendto(b"SYN-ACK",address_client)    # Envoi du SYN-ACK
    print()
    print("***************** Reception de l'ACK **********************")
    print()
    data, adresse = socket.recvfrom(1024)   # Reception du ACK

    if data == b"ACK":
        print("ACK reçu")
        print()
        print("***************** Fin du processus de poignée de main **********************")
        print()
        print("Connexion établie avec {}".format(adresse))
    else:
        print("ACK non reçu")
        print("Echec du processus de poignée de main")
 

# Fonction pour l'envoi de fichier
def EnvoiFichier(socket, adresse, nom_fichier):
    print("***************** Envoi du fichier **********************")
    print()
    with open(nom_fichier, "rb") as fichier:     # Ouverture du fichier en mode lecture binaire
        morçeau = fichier.read(1024)        # Lecture des octets
        while morçeau:        # Boucle pour lire tous les octets
            socket.sendto(morçeau, adresse)      # Envoi des octets
            morçeau = fichier.read(1024)        # Lecture des octets pour controler la boucle
    print("Fichier envoyé")        # Affichage visuel de l'état du serveur
    print()


# Création du socket UDP
hote, port = ('localhost', 2212)     # address serveur
address_client = ('localhost', 2213)     # address client

sock_servr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # Création du socket de type SOCK_DGRAM pour UDP
sock_servr.bind((hote, port))        # Liaison du socket à une adresse IP et un port


message_confirmation = b"Message bien recu"

# Boucle infinie pour recevoir les messages des clients
while True:
    data, adresse = sock_servr.recvfrom(1024)   # Reception demande de connection
    data = data.decode('utf-8')

    if not data:
        print()
        print("Le serveur est en écoute sur le port {}".format(port))      # Affichage visuel de l'état du serveur
        print()
        print("En attente d'une demande de connection")
        print()
    elif data == "open localhost" or data == "open 127.0.0.1":
        print("Demande de connection reçue de la part de {}".format(adresse))
        print()
        ProcessusPoigneDeMain(sock_servr)        # Appel de la fonction ProcessusPoigneDeMain
        print()
        print()
        #print("*"*40)
    elif data == "ls":
        print()
        #data, adresse = sock_servr.recvfrom(1024)                           # Réception des données
        #print("Message reçu : {} de la part de {}".format(data, adresse))     # Affichage visuel des données reçues
        #sock_servr.sendto(message_confirmation,address_client)                      # Réponse au client
        print("Execution de la commande <ls>")                    # Affichage visuel de l'état du serveur
        print()

    elif data == "get":
        print()
        print("Execution de la commande <get>")                    # Affichage visuel de l'état du serveur
        print()
    
    elif data == "bye":
        print()
        sock_servr.close()                               # Fermeture du socket
        #print("socket")                  # Affichage visuel de l'état du serveur
        print("Connexion au serveur terminé")            # Affichage visuel de l'état du serveur
        break
    else:
        print()
        print("Commande non reconnue")
        print()







