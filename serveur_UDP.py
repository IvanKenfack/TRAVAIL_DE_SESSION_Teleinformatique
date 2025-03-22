
import socket
import struct
import os
from hashlib import sha1
import random



# Création du socket serveur

# Definition des parametres de connexion
hote, port = ('localhost', 2212)     
address_client = ('localhost', 2213)

# Création du socket de type SOCK_DGRAM
sock_servr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liaison du socket à une adresse IP et un port        
sock_servr.bind((hote, port)) 



#Parametres de l'entête

#Numero de sequence
numero_seq = 0
#Numero d'acquittement
numero_ack = 0
#Drapeau/code de controle
drapeau = b""

#tailleMorçeau generé aléatoirement pour simuler également la mutabilité de ce dernier dependament de la connexion
tailleMorçeau =random.randint(274,280)     #204874 

#Taille de la fenetre generé aléatoirement pour simuler la mutabilité de ce dernier dependament de la connexion
# limité entre le tailleMorçeau et tailleMorçeau*2 pour éviter de gérer le windows scaling le serveur ne recois pas grand chose du client
fenetrage_srvr = random.randint(274,548)
#fentrage recu du client
fenetrage_clt = 0

checksum = b""
nom_fichier = b""
donnee = b""


#Fonction du generateur de signature hash
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



#Definition parametre format de struct.pack
# numero_seq(4 octets), numero_ack(4 octets), drapeau(3 octets), tailleMorçeau(4 octets), checksum(40 octets), nom_fichier(15 octets), donnee(204800 octets)
format_entete = "!I I 3s I I 40s 15s 200s"     

#Definition de la fonction de creation de segment
def CreationSegment(numero_seq, numero_ack, drapeau, fenetrage_srvr, tailleMorçeau, checksum, nom_fichier, donnee):

    #Empaquetage des parametres du segment
    segment = struct.pack(format_entete, numero_seq, numero_ack, drapeau, fenetrage_srvr, tailleMorçeau, checksum, nom_fichier, donnee)
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


# Fonction pour l'initiation de la connexion (processus de Three-way handshake)
def ProcessusInitiationConnexion(socket):

    #Pour le passage par reference
    global fenetrage_clt,fenetrage_srvr,tailleMorçeau
    print()
    print("***************** Processus de poignée de main coté serveur **********************")
    print() 
    print()
    # Reception du segment SYN
    donnée, adresse = socket.recvfrom(1024)
    
    # Extraction des informations du segment
    numero_seq, numero_ack, drapeau, fenetrage1, mss1, checksum, nom_fichier, donnee = struct.unpack(format_entete, donnée)

    #Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")
    
    #Modification du fenetrage client
    fenetrage_clt = fenetrage1

    #Si l'intégrité des données est correct, le SYN_ACK est envoyé
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("SYN reçu")
        print()
        print("Numero de sequence : {}".format(numero_seq))
        print("Numero d'acquittement : {}".format(numero_ack))
        print("Drapeau : {}".format(drapeau))
        print("Fenetrage_client : {}".format(fenetrage1))
        print("Taille morçeau : {}".format(mss1))     
        print()

        #Creation et envoi du segment SYN-ACK / Negociation des parametres
        segment = CreationSegment(0, 1, b"ACK", fenetrage_srvr, tailleMorçeau, signature_SYN_ACK, b"", b"SYN-ACK")
        EnvoiMessage(socket, segment, address_client)    # Envoi du SYN-ACK
        print("SYN-ACK envoyé")
        print()

    #Sinon il y'a affichage d'un message d'erreur
    else:
        print("SYN non reçu")
        print("Echec du processus de poignée de main")
        print()
    
    # Reception du ACK
    donnée, adresse = socket.recvfrom(1024)   # Reception du ACK

     # Extraction des informations du segment
    numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau, checksum, nom_fichier, donnee = struct.unpack(format_entete, donnée)

    #Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")

    #Verification de l'integrité du segment et affichage de l'état du client
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("ACK reçu")
        print()
        print("Numero de sequence : {}".format(numero_seq))
        print("Numero d'acquittement : {}".format(numero_ack))
        print("Drapeau : {}".format(drapeau))
        print("Fenetrage : {}".format(fenetrage1))
        print("Taille morçeau : {}".format(tailleMorçeau)) 
        print()
        sock_servr.connect(address_client)
        print("Connexion établie avec success a {}".format(adresse))
        print()
        print()
        print(f'''*** Parametres negocié: ***
            Taille_morceau : {tailleMorçeau} 
            Fenetrage_client : {fenetrage_clt}
            Fenetrage_serveur : {fenetrage_srvr}''')
        print()
        print()

    else:
        print("ACK non reçu")
        print("Echec du processus de poignée de main")
        print()
    

    
# Fonction pour l'envoi de fichier
def EnvoiFichier(socket, adresse, nom_fichier):
    print()
    print("***************** Envoi du fichier **********************")
    print()
    with open(nom_fichier, "rb") as fichier:     # Ouverture du fichier en mode lecture binaire
        morçeau = fichier.read(1024)        # Lecture des octets
        while morçeau:        # Boucle pour lire tous les octets
            socket.sendto(morçeau, adresse)      # Envoi des octets
            morçeau = fichier.read(1024)        # Lecture des octets pour controler la boucle
    print("Fichier envoyé")        # Affichage visuel de l'état du serveur
    print()

 
print()
print("Le serveur est en écoute sur le port {}".format(port))      # Affichage visuel de l'état du serveur
print()
print("En attente d'une demande de connection")
print()

# Boucle infinie pour recevoir les messages des clients
while True:
    commande, adresse = sock_servr.recvfrom(1024)   # Reception demande de connection
    commande = commande.decode('utf-8')
    
    # si commande = open localhost ou open 127.0.0.1
    if commande == "open localhost" or commande == "open 127.0.0.1" or commande == "1":
        print("Demande de connection reçue de la part de {}".format(adresse))
        print()
        ProcessusInitiationConnexion(sock_servr)        # Appel de la fonction ProcessusInitiationConnexion
        print()
        print()
        #print("*"*40)
        
    # si commande = ls
    elif commande == "ls" or commande == "2":
        print()
        print("Execution de la commande <ls>")
        print()
        print(os.listdir("Dossier_Travail"))

        #Recuperation de la liste du contenu du repertoire cible
        données = os.listdir("Dossier_Travail")
        
        #Conversion de la liste en chaine de caractere
        données = "\n".join(données)

        #Envoi de la liste des fichiers
        sock_servr.send(données.encode('utf-8'))
        print()
        print("Liste des fichiers envoyée")
        print()
        print()
        
    #si commande = get
    elif commande == "get" or commande == "3":
        print()
        print("Execution de la commande <get>")                    # Affichage visuel de l'état du serveur
        print()
        
    #Si commande = bye
    elif commande == "bye" or commande == "4":
        print()
        sock_servr.close()                               # Fermeture du socket
        #print("socket")                  # Affichage visuel de l'état du serveur
        print("Connexion au serveur terminé")            # Affichage visuel de l'état du serveur
        break
    
    #Erreur d'entrée
    else:
        print()
        print("Commande non reconnue")
        print()
        continue







