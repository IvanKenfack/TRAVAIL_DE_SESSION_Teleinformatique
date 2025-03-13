
import socket
import struct

#Definition de la structure de l'entête
format_entete = "!I I 3s I I 40s 15s 204800s"     # network byte order numero_seq(4 octets), numero_ack(4 octets), drapeau(3 octets), mss(4 octets), checksum(40 octets), nom_fichier(15 octets), morceau_fichier(204800 octets)

#Parametres de l'entête
numero_seq = 0
numero_ack = 0
drapeau = b""
fenetrage = 0
mss = 0
checksum = b""
nom_fichier = b""
morceau_fichier = b""

#Definition de la fonction de creation de segment
def CreationSegment(numero_seq, numero_ack, drapeau, fenetrage, mss, checksum, nom_fichier, morceau_fichier):
    segment = struct.pack(format_entete, numero_seq, numero_ack, drapeau, fenetrage, mss, checksum, nom_fichier, morceau_fichier)
    return segment


# Creation du socket client
hote, port = ('localhost', 2213)     # Même couple hote/port que celui du serveur
sock_client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # Création du socket de type UDP
address_serveur = ('localhost', 2212)     # Adresse du serveur
sock_client1.bind((hote, port))       # Liaison du socket à une adresse IP et un  port


def ProcessusPoigneDeMain(socket, segment):
    print
    print("********* Processus de poignée de main **************")
    print()
    print("***************** Envoi du segment SYN **********************")
    print()
    socket.sendto(segment, address_serveur)    # Envoi du SYN
    print("SYN envoyé")
    print()
    print("************* Réception du SYN-ACK ******************")
    print()
    donnée, adresse = socket.recvfrom(1024)    # Réception du SYN-ACK
    donnée = donnée.decode('UTF-8')    # Décodage du SYN-ACK
    print(donnée,"réçu")     # Affichage visuel du SYN-ACK
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
    print()
    print("*"*50)
    print()
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
        #donnée, adresse = sock_client1.recvfrom(1024)    # Réception de la réponse
        #print(donnée)     # Affichage visuel de la réponse
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

