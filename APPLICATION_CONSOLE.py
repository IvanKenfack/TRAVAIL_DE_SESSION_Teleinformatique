
import socket

hote, port = ('localhost', 2213)     # Même couple hote/port que celui du serveur
sock_client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # Création du socket UDP
address_serveur = ('localhost', 2212)     # Adresse du serveur

sock_client1.bind((hote, port))       # Liaison du socket à une adresse IP et un  port


def ProcessusPoigneDeMain(socket):
    print("***************** Processus de poignée de main **********************")
    print()
    print("***************** Envoi du SYN **********************")
    print()
    socket.sendto(b"SYN", address_serveur)    # Envoi du SYN
    print("SYN envoyé")
    print()
    print("***************** Réception du SYN-ACK **********************")
    print()
    data, adresse = socket.recvfrom(1024)    # Réception du SYN-ACK
    print(data)     # Affichage visuel du SYN-ACK
    print()
    print("***************** Envoi de l'ACK **********************")
    print()
    socket.sendto(b"ACK", address_serveur)    # Envoi de l'ACK
    print("ACK envoyé")
    print()
    print("***************** Fin du processus de poignée de main **********************")
    print() 
    print("Connexion établie avec {}".format(adresse))    # Affichage visuel de l'état du serveur
    print()

while True:
    print("Que voulez vous faire?")
    print()
    print("Les commandes suivantes sont disponibles:")
    print()
    print("open <addressIP>")
    print("ls")
    print("get")
    print("bye")
    print()
    print("Veuillez entrer une commande")
    print()
    commande = input("Commande: ")
    print()

    if commande == "bye":        # Condition pour arrêter la connexion
        sock_client1.sendto(commande.encode(), address_serveur)    # Envoi de la commande
        sock_client1.close()    # Fermeture du socket
        print("Connexion fermée")    # Affichage visuel de la connexion fermée
        break

    if commande == "ls":
        sock_client1.sendto(commande.encode(), address_serveur)    # Envoi de la commande
        #print(f"Commande envoyée : {commande}")    # Affichage visuel de la commande envoyée
        print()
        #ProcessusPoigneDeMain(sock_client1)        # Appel de la fonction ProcessusPoigneDeMain
        print()
        data, adresse = sock_client1.recvfrom(1024)    # Réception de la réponse
        print(data)     # Affichage visuel de la réponse
        print()

    elif commande == "open localhost" or commande == "open 127.0.0.1":
        sock_client1.sendto(commande.encode(), address_serveur)    # Envoi de la commande
        ProcessusPoigneDeMain(sock_client1)        # Appel de la fonction ProcessusPoigneDeMain



    elif commande == "get":
        nom_fichier = input("Entrez le nom du fichier à télécharger: ")
        print() 
        sock_client1.sendto(commande.encode(), address_serveur)    # Envoi de la commande

    else:
        print("Commande inconnue")
        print()

    #connexion au serveur
    #sock_client1.connect(address_serveur)
    #message = b"Bonjour le monde!"    # Message à envoyer

    #for i in range(5):
    #   print()
    #  sock_client1.send(message)     # Envoi du message
    # print(f"Message envoyé : {message}")    # Affichage visuel du message envoyé
        #print()
        #print("***************** Message du serveur **********************")
        #print()
        #data, adresse = sock_client1.recvfrom(1024)    # Réception de la réponse
        #print(data)     # Affichage visuel de la réponse
        #print()

