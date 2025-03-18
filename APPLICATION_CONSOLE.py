
import socket
import struct
from hashlib import sha1
import random


# Creation du socket client

# Definition des parametres de connexion
hote, port = ('localhost', 2213)

# Creation du socket de type SOCK_DGRAM
sock_client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Definition des parametres de connexion
address_serveur = ('localhost', 2212)

# Liaison du socket à une adresse IP et un port
sock_client1.bind((hote, port))


#Parametres de l'entête du segment

#Numero de sequence
numero_seq = 0   
#Numero d'acquittement
numero_ack = 0
#Drapeau/code de controle
drapeau = b""
#Taille maximal du segment/Maximum segment size
tailleMorçeau = random.randint(274,280)
#Taille de la fenetre du client
fenetrage = random.randint(65486,65536)     #tailleMorçeau * 239  #65486

#fenetrage serveur
fenetrage_srvr = 0

checksum = b""
nom_fichier = b""
donnee = b""


#Definition du parametre format de struct.pack
# network byte order numero_seq(4 octets), numero_ack(4 octets), drapeau(3 octets), tailleMorçeau(4 octets), checksum(40 octets), nom_fichier(15 octets), donnee({tailleMorceau} octets)
format_entete = f"!I I 3s I I 40s 15s 200s"     

#Definition de la fonction de creation de segment
def CreationSegment(numero_seq, numero_ack, drapeau, fenetrage, tailleMorçeau, checksum, nom_fichier, donnee):

    #Empaquetage des parametres du segment
    segment = struct.pack(format_entete, numero_seq, numero_ack, drapeau, fenetrage, tailleMorçeau, checksum, nom_fichier, donnee)
    return segment


#Definition de la fonction d'envoi de message avec gestion d'erreur
def EnvoiMessage(socket, message, adresse):

    try:
        socket.sendto(message, adresse)    # Envoi du message
        #print("Message envoyé")    # Affichage visuel de l'état du serveur

    except OSError:
        print("Taille du message trop grande")

    except:
        print(f"Erreur inconnue lors de l'envoi du message")    # Affichage visuel de l'erreur



#Definition du generateur du checksum/hash avec la fonction de hachage sha1
def GenerateurSignatureHash(donnee):

    #initialisation de l'objet sha1
    objet_sha1 = sha1()

    #mise a jour de l'objet sha1 avec les donnees
    objet_sha1.update(donnee)

    #generation de la signature
    signature = objet_sha1.digest()

    #retourne la signature
    return signature


#Calcul et assignation des signatures de quelques parametres
signature_SYN = GenerateurSignatureHash(b"SYN")
signature_ACK = GenerateurSignatureHash(b"ACK")
signature_SYN_ACK = GenerateurSignatureHash(b"SYN-ACK")


# Fonction pour l'initiation de la connexion (processus de Three-way handshake)
def ProcessusPoigneDeMain(socket):

    #Pour le passage par reference
    global tailleMorçeau,fenetrage_srvr,fenetrage
    
    print()
    print("********* Processus de poignée de main coté client **************")

    # Création du segment SYN
    segment = CreationSegment(0,0,b"SYN",fenetrage,tailleMorçeau,signature_SYN,b"",b"SYN")
    print()    
    print()
    # Envoi du SYN
    EnvoiMessage(socket, segment, address_serveur)
    print("SYN envoyé")
    print()
    print()

    # Réception du SYN-ACK
    données, adresse = socket.recvfrom(1024)
    
     # Extraction des informations du segment
    numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau1, checksum, nom_fichier, donnee = struct.unpack(format_entete, données)

    #Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")
    
    #Modification fenetrage serveur
    fenetrage_srvr = fenetrage1

    #Si l'intégrité des données est correct, le ACK est envoyé
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("SYN_ACK reçu")
        print()
        print("Numero de sequence : {}".format(numero_seq))
        print("Numero d'acquittement : {}".format(numero_ack))
        print("Drapeau : {}".format(drapeau))
        print("Fenetrage_serveur : {}".format(fenetrage1))
        print("MSS : {}".format(tailleMorçeau1)) 
        print()

        #Logique de négociation
        if tailleMorçeau1 < tailleMorçeau:
            tailleMorçeau = tailleMorçeau1  

        #Creation et envoi du segment ACK / Finalisation  de la connexion
        segment = CreationSegment(1, 1, b"ACK", fenetrage, tailleMorçeau, signature_ACK, b"", b"ACK")
        EnvoiMessage(socket, segment, address_serveur)
        print("ACK envoyé")
        print()
      
    #Sinon il y'a affichage d'un message d'erreur
    else:
        print("SYN non reçu")
        print("Echec du processus de poignée de main")
        print()
    
    print()
    sock_client1.connect(address_serveur) 
    print("Connexion établie avec success a {}".format(address_serveur))
    print()
    print(f'''*** Parametres negocié: ***
            Taille_morceau : {tailleMorçeau} 
            Fenetrage_client : {fenetrage}
            Fenetrage_serveur : {fenetrage_srvr}''')

# Boucle infinie pour l'envoi des commandes
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
        #données, adresse = sock_client1.recvfrom(1024)    # Réception de la réponse
        #print(données)     # Affichage visuel de la réponse
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

