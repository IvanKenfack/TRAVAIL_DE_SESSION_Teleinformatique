"""import socket
import struct
import os
from hashlib import sha1
import random
from tqdm import tqdm



# Création du socket serveur

# Definition des parametres de connexion
hote, port = ('localhost', 2212)
address_client = ('localhost', 2213)

# Création du socket de type SOCK_DGRAM
sock_servr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liaison du socket à une adresse IP et un port
sock_servr.bind((hote, port))


##############################################################################################################
#                #CONFIGURATIONS

#Nombre d'essai maximal d'envoi de segment
ESSAIES_MAX = 5

#Delai d'attente maximal pour la reception d'un segment
DELAI_MAX = 3

#Fiabilité du reseau
FIABILITE = 1#round(random.choice([0.95, 1.0]),2) #remplacer par 1.0 pour simuler un reseau fiable
print(f"Fiabilité du reseau: {FIABILITE}")
print()

#Parametres de l'entête

#Commande
commande = b""
#Numero de sequence
numero_seq = 0
#Numero d'acquittement
numero_ack = 0
#Drapeau/code de controle
drapeau = b""

#tailleMorçeau generé aléatoirement pour simuler également la mutabilité de ce dernier dependament de la connexion
tailleMorçeau = 200 #random.randint(274,280)     #204874

#Taille de la fenetre generé aléatoirement pour simuler la mutabilité de ce dernier dependament de la connexion
# limité entre la tailleMorçeau et tailleMorçeau*2 pour éviter de gérer le windows scaling le serveur ne recois pas grand chose du client
fenetrage_srvr = random.randint(274,548)
#fentrage recu du client
fenetrage_clt = 0

checksum = b""
nom_fichier = b""
donnee = b""


#################################################################################################



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
format_entete = "!25s I I 3s I I 40s 24s 920s"

#Definition de la fonction de creation de segment
def CreationSegment(commande,numero_seq, numero_ack, drapeau, fenetrage_srvr, tailleMorçeau, checksum, nom_fichier, donnee):

    #Empaquetage des parametres du segment
    segment = struct.pack(format_entete, commande, numero_seq, numero_ack, drapeau, fenetrage_srvr, tailleMorçeau, checksum, nom_fichier, donnee)
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

############################################################################################################


# Fonction pour l'initiation de la connexion (processus de Three-way handshake)
def ProcessusInitiationConnexion(socket):

    #Pour le passage par reference
    global fenetrage_clt,fenetrage_srvr,tailleMorçeau, numero_ack,numero_seq
    print()
    print("***************** Processus de poignée de main coté serveur **********************")
    print()
    print()
    # Reception du segment SYN
    donnée, adresse = socket.recvfrom(1029)

    # Extraction des informations du segment
    commande,numero_seq, numero_ack, drapeau, fenetrage1, mss1, checksum, nom_fichier, donnee = struct.unpack(format_entete, donnée)

    #Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")
    print(donnee)
    #Modification du fenetrage client
    fenetrage_clt = fenetrage1

    #print(f"Checksum recu: {checksum}")

    #Si l'intégrité des données est correct, le SYN_ACK est envoyé
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("SYN reçu")
        print()
        print("Numero de sequence reçu: {}".format(numero_seq))
        #print("Numero d'acquittement : {}".format(numero_ack))
        print("Drapeau reçu: {}".format(drapeau))
        print("Fenetrage_client reçu: {}".format(fenetrage1))
        print("Taille morçeau reçu: {}".format(mss1))
        print()

        numero_ack = numero_seq + 1

        #Creation et envoi du segment SYN-ACK / Negociation des parametres
        segment = CreationSegment(b"",numero_seq,numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau, signature_SYN_ACK, b"", b"SYN-ACK")

        EnvoiMessage(socket, segment, address_client)    # Envoi du SYN-ACK
        print("SYN-ACK envoyé")
        print()

        #On attends une confirmation de reception(SYN-ACK) pendant 3 secondes
        socket.settimeout(DELAI_MAX)
        try:
            # Réception du ACK
            données, adresse = socket.recvfrom(1029)
            print("SYN-ACK reçu")
            print()

        # Si le segment n'est pas reçu dans le delai imparti, on renvoie le segment SYN a 5 reprises
        except socket.timeout:
            print("Delai d'attente depassé")
            print()
            print("Reexpedition du segment SYN-ACK ")
            print()

            for index in range(ESSAIES_MAX):
                EnvoiMessage(socket, segment, address_serveur)
                print("SYN réenvoyé")
                print()
                socket.settimeout(DELAI_MAX)
                try:
                    données, adresse = socket.recvfrom(1029)
                    break
                except socket.timeout:
                    if index == ESSAIES_MAX - 1:
                        print("Echec de la connexion")
                        print()
                        print("Connexion terminée")
                        socket.close()
                        return

                    print("Delai d'attente depassé")
                    print()
                    print("Tentative de reexpedition du segment SYN-ACK numero {}".format(index+1))
                    continue

    #Sinon il y'a affichage d'un message d'erreur
    else:
        print("SYN reçu corrompu")

        print("Echec du processus de poignée de main")
        print()

    # Reception du ACK
   # donnée, adresse = socket.recvfrom(1029)   # Reception du ACK

     # Extraction des informations reçues
    commande,numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau, checksum, nom_fichier, donnee = struct.unpack(format_entete, données)

    #Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")

    #Verification de l'integrité du segment et affichage de l'état du client
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("ACK reçu")
        print()
        print("Numero de sequence reçu: {}".format(numero_seq))
        print("Numero d'acquittement reçu: {}".format(numero_ack))
        print("Drapeau reçu: {}".format(drapeau))
        print("Fenetrage reçu: {}".format(fenetrage1))
        print("Taille morçeau reçu: {}".format(tailleMorçeau))
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
        print("ACK mal reçu")
        print("Echec du processus de poignée de main")
        print()



############################################################################################################


# Fonction pour l'envoi de fichier
def EnvoiFichier(socket, nom_fichier):
    global fenetrage_clt,tailleMorçeau
    print()
    print("***************** Envoi du fichier **********************")
    print()

    # Envoi du fichier
    with open (nom_fichier, "rb") as fichier:    # Ouverture du fichier en mode lecture binaire
        morçeau = fichier.read(930)
        i = 0               # Lecture des octets
        while morçeau:
                #print (f"Iteration {i+1}, taille morceau : {len(morçeau)}")
                                            # Boucle pour lire tous les octets
                segment =  CreationSegment(b"",numero_seq, numero_ack, b"", fenetrage_srvr, len(morçeau), GenerateurSignatureHash(morçeau), b"", morçeau)
                socket.send(segment)         # Envoi des octets
                morçeau = fichier.read(930)        # Lecture des octets pour controler la boucle
                i += 1

        # Envoi du segment de fin
        segment = CreationSegment(b"",numero_seq, numero_ack, b"FIN", fenetrage_srvr, tailleMorçeau, GenerateurSignatureHash(b"FIN"), b"", b"")
        socket.send(segment)         # Envoi du segment de fin
        print("Fichier envoyé")
    print()


############################################################################################################


def EnvoiMessageAvecConnexion(socket, message):

    #si le reseau est fiable, on envoie le message
    if FIABILITE == 1.0:
        # Envoi du message
        try:
            socket.send(message)    # Envoi du message
            print("Message envoyé")
            print()
        except OSError:
            print("Taille du message trop grande")

        except:
            print(f"Erreur inconnue lors de l'envoi du message")
            return
    #sinon on simule une perte de message
    else:
        print("Message perdu")
        return


################################################################################################################


                            #PROGRAMME PRINCIPAL


# Affichage visuel de l'état initial du serveur
print()
print("Le serveur est en écoute sur le port {}".format(port))      # Affichage visuel de l'état du serveur
print()
print("En attente d'une demande de connection")
print()

segment = CreationSegment(b"ACK", numero_seq, numero_ack+1, b"", fenetrage_srvr, tailleMorçeau, GenerateurSignatureHash(b"SYN"), b"", b"SYN")

# Boucle infinie pour recevoir les messages des clients
while True:
    #Je limite l'effet du timeout uniquement sur le if et non le while
    sock_servr.settimeout(None)

    # Réception du segment
    segment, adresse = sock_servr.recvfrom(1029)

    # Extraction des informations du segment
    commande,numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau, checksum, nom_fichier, donnee = struct.unpack(format_entete, segment)

    # Nettoyage de la commande
    commande = commande.rstrip(b"\x00")
    commande = commande.decode('utf-8')

    print("Commande reçue: {}".format(commande))    # Affichage de la commande reçue

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

        numero_ack = numero_seq + 1
        #Creation et envoi du segment ACK
        segment = CreationSegment(b"",numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau, GenerateurSignatureHash(b"ACK"), b"", b"ACK")
        EnvoiMessageAvecConnexion(sock_servr, segment)    # Envoi du segment ACK
        print("ACK envoyé")
        print()


        print("Execution de la commande <ls>")
        print()
        print(os.listdir("Dossier_Travail"))

        #Recuperation de la liste du contenu du repertoire de fichiers
        données = os.listdir("Dossier_Travail")

        #Conversion de la liste en chaine de caractere
        données = "\n".join(données)

        #Envoi de la liste des fichiers
        données = données.encode('utf-8')
        segment = CreationSegment(b"",numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau, GenerateurSignatureHash(données), b"", données)
        EnvoiMessageAvecConnexion(sock_servr, segment)    # Envoi de la liste des fichiers
        print()
        print("Liste des fichiers envoyée")
        print()
        print()

    #si commande = get
    elif commande == "get" or commande == "3":
        print()
        numero_ack = numero_seq + 1
        #Creation et envoi du segment ACK
        segment = CreationSegment(b"",numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau, GenerateurSignatureHash(b"ACK"), b"", b"ACK")
        EnvoiMessageAvecConnexion(sock_servr, segment)    # Envoi du segment ACK
        print("ACK envoyé")
        print()
        print()
        print("Execution de la commande <get>")                    # Affichage visuel de l'état du serveur
        print()

        nom_fichier = nom_fichier.rstrip(b"\x00")

        #Decodage du nom du fichier
        nom_fichier = nom_fichier.decode('utf-8')
        print("Nom du fichier demandé: {}".format(nom_fichier))
        print()
        EnvoiFichier(sock_servr, nom_fichier)
        #print(f"fenetrage_clt : {fenetrage_clt}")
        #print()



    #Si commande = bye
    elif commande == "bye" or commande == "4":
        print()

        EnvoiMessageAvecConnexion(sock_servr, segment)    # Envoi du segment ACK
        print("ACK envoyé")

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






"""

import socket
import struct
import os
from hashlib import sha1
import random
from tqdm import tqdm

# Création du socket serveur

# Definition des parametres de connexion
hote, port = ('localhost', 2212)
address_client = ('localhost', 2213)

# Création du socket de type SOCK_DGRAM
sock_servr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Liaison du socket à une adresse IP et un port
sock_servr.bind((hote, port))

##############################################################################################################
#                #CONFIGURATIONS

# Nombre d'essai maximal d'envoi de segment
ESSAIES_MAX = 5

# Delai d'attente maximal pour la reception d'un segment
DELAI_MAX = 3

# Fiabilité du reseau
FIABILITE = 1  # round(random.choice([0.95, 1.0]),2) #remplacer par 1.0 pour simuler un reseau fiable
print(f"Fiabilité du reseau: {FIABILITE}")
print()

# Parametres de l'entête

# Commande
commande = b""
# Numero de sequence
numero_seq = 0
# Numero d'acquittement
numero_ack = 0
# Drapeau/code de controle
drapeau = b""

# tailleMorçeau generé aléatoirement pour simuler également la mutabilité de ce dernier dependament de la connexion
tailleMorçeau = 200  # random.randint(274,280)     #204874

# Taille de la fenetre generé aléatoirement pour simuler la mutabilité de ce dernier dependament de la connexion
# limité entre la tailleMorçeau et tailleMorçeau*2 pour éviter de gérer le windows scaling le serveur ne recois pas grand chose du client
fenetrage_srvr = random.randint(274, 548)
# fentrage recu du client
fenetrage_clt = 0

checksum = b""
nom_fichier = b""
donnee = b""


#################################################################################################


# Fonction du generateur de signature hash
def GenerateurSignatureHash(donnee):
    # initialisation de l'objet sha1
    objet_sha1 = sha1()

    # mise a jour de l'objet sha1 avec les donnees
    objet_sha1.update(donnee)

    # generation de la signature
    signature = objet_sha1.digest()

    # retourne la signature
    return signature


# Calcul et assignation des signatures de quelques parametres
signature_SYN = GenerateurSignatureHash(b"SYN")
signature_ACK = GenerateurSignatureHash(b"ACK")
signature_SYN_ACK = GenerateurSignatureHash(b"SYN-ACK")

# Definition parametre format de struct.pack
# numero_seq(4 octets), numero_ack(4 octets), drapeau(3 octets), tailleMorçeau(4 octets), checksum(40 octets), nom_fichier(15 octets), donnee(204800 octets)
format_entete = f"!25s I I 3s I I 40s 25s 920s"


# Definition de la fonction de creation de segment
def CreationSegment(commande, numero_seq, numero_ack, drapeau, fenetrage_srvr, tailleMorçeau, checksum, nom_fichier,
                    donnee):
    # Empaquetage des parametres du segment
    segment = struct.pack(format_entete, commande, numero_seq, numero_ack, drapeau, fenetrage_srvr, tailleMorçeau,
                          checksum, nom_fichier, donnee)
    return segment


# Definition de la fonction d'envoi de message avec gestion d'erreur
def EnvoiMessage(socket, message, adresse):
    try:
        socket.sendto(message, adresse)  # Envoi du message
        # print("Message envoyé")    # Affichage visuel de l'état du serveur

    except OSError:
        print("Taille du message trop grande")

    except:
        print(f"Erreur inconnue lors de l'envoi du message")  # Affichage visuel de l'erreur


############################################################################################################


# Fonction pour l'initiation de la connexion (processus de Three-way handshake)
def ProcessusInitiationConnexion(socket):
    # Pour le passage par reference
    global fenetrage_clt, fenetrage_srvr, tailleMorçeau, numero_ack, numero_seq
    print()
    print("***************** Processus de poignée de main coté serveur **********************")
    print()
    print()
    # Reception du segment SYN
    donnée, adresse = socket.recvfrom(1029)

    # Extraction des informations du segment
    commande, numero_seq, numero_ack, drapeau, fenetrage1, mss1, checksum, nom_fichier, donnee = struct.unpack(
        format_entete, donnée)

    # Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")
    print(donnee)
    # Modification du fenetrage client
    fenetrage_clt = fenetrage1

    # print(f"Checksum recu: {checksum}")

    # Si l'intégrité des données est correct, le SYN_ACK est envoyé
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("SYN reçu")
        print()
        print("Numero de sequence reçu: {}".format(numero_seq))
        # print("Numero d'acquittement : {}".format(numero_ack))
        print("Drapeau reçu: {}".format(drapeau))
        print("Fenetrage_client reçu: {}".format(fenetrage1))
        print("Taille morçeau reçu: {}".format(mss1))
        print()

        numero_ack = numero_seq + 1

        # Creation et envoi du segment SYN-ACK / Negociation des parametres
        segment = CreationSegment(b"", numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau, signature_SYN_ACK,
                                  b"", b"SYN-ACK")

        EnvoiMessage(socket, segment, address_client)  # Envoi du SYN-ACK
        print("SYN-ACK envoyé")
        print()

        # On attends une confirmation de reception(SYN-ACK) pendant 3 secondes
        socket.settimeout(DELAI_MAX)
        try:
            # Réception du ACK
            données, adresse = socket.recvfrom(1029)
            print("SYN-ACK reçu")
            print()

        # Si le segment n'est pas reçu dans le delai imparti, on renvoie le segment SYN a 5 reprises
        except socket.timeout:
            print("Delai d'attente depassé")
            print()
            print("Reexpedition du segment SYN-ACK ")
            print()

            for index in range(ESSAIES_MAX):
                EnvoiMessage(socket, segment, address_client)
                print("SYN réenvoyé")
                print()
                socket.settimeout(DELAI_MAX)
                try:
                    données, adresse = socket.recvfrom(1029)
                    break
                except socket.timeout:
                    if index == ESSAIES_MAX - 1:
                        print("Echec de la connexion")
                        print()
                        print("Connexion terminée")
                        socket.close()
                        return

                    print("Delai d'attente depassé")
                    print()
                    print("Tentative de reexpedition du segment SYN-ACK numero {}".format(index + 1))
                    continue

    # Sinon, il y a affichage d'un message d'erreur
    else:
        print("SYN reçu corrompu")

        print("Echec du processus de poignée de main")
        print()

    # Reception du ACK
    # donnée, adresse = socket.recvfrom(1029)   # Reception du ACK

    # Extraction des informations reçues
    commande, numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau, checksum, nom_fichier, donnee = struct.unpack(
        format_entete, données)

    # Nettoyage des donnees
    donnee = donnee.rstrip(b"\x00")

    # Verification de l'integrité du segment et affichage de l'état du client
    if GenerateurSignatureHash(donnee) == checksum.rstrip(b"\x00"):
        print("ACK reçu")
        print()
        print("Numero de sequence reçu: {}".format(numero_seq))
        print("Numero d'acquittement reçu: {}".format(numero_ack))
        print("Drapeau reçu: {}".format(drapeau))
        print("Fenetrage reçu: {}".format(fenetrage1))
        print("Taille morçeau reçu: {}".format(tailleMorçeau))
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
        print("ACK mal reçu")
        print("Echec du processus de poignée de main")
        print()


############################################################################################################


# Fonction pour l'envoi de fichier
def EnvoiFichier(socket, nom_fichier):
    global fenetrage_clt, tailleMorçeau

    taille_fichier = os.path.getsize(nom_fichier)
    print()
    print("***************** Envoi du fichier **********************")
    print()

    # Envoi du fichier
    with open(nom_fichier, "rb") as fichier:  # Ouverture du fichier en mode lecture binaire
        morçeau = fichier.read(930)
        #Initialisation bar de progression TQDM
        with tqdm(total = taille_fichier, unit ='B',unit_scale=True,desc="Envoi", ncols=80) as pbar:
            while morçeau:
                # print (f"Iteration {i+1}, taille morceau : {len(morçeau)}")
                # Boucle pour lire tous les octets
                segment = CreationSegment(b"", numero_seq, numero_ack, b"", fenetrage_srvr, len(morçeau),
                                          GenerateurSignatureHash(morçeau), b"", morçeau)
                socket.send(segment)  # Envoi des octets
                pbar.update(len(morçeau))
                morçeau = fichier.read(930)  # Lecture des octets pour controler la boucle

        # Envoi du segment de fin
        segment = CreationSegment(b"", numero_seq, numero_ack, b"FIN", fenetrage_srvr, tailleMorçeau,
                                  GenerateurSignatureHash(b"FIN"), b"", b"")
        socket.send(segment)  # Envoi du segment de fin
        print("Fichier envoyé")
    print()


############################################################################################################


def EnvoiMessageAvecConnexion(socket, message):
    # si le reseau est fiable, on envoie le message
    if FIABILITE == 1.0:
        # Envoi du message
        try:
            socket.send(message)  # Envoi du message
            print("Message envoyé")
            print()
        except OSError:
            print("Taille du message trop grande")

        except:
            print(f"Erreur inconnue lors de l'envoi du message")
            return
    # sinon on simule une perte de message
    else:
        print("Message perdu")
        return


################################################################################################################


# PROGRAMME PRINCIPAL


# Affichage visuel de l'état initial du serveur
print()
print("Le serveur est en écoute sur le port {}".format(port))  # Affichage visuel de l'état du serveur
print()
print("En attente d'une demande de connection")
print()

segment = CreationSegment(b"ACK", numero_seq, numero_ack + 1, b"", fenetrage_srvr, tailleMorçeau,
                          GenerateurSignatureHash(b"SYN"), b"", b"SYN")

# Boucle infinie pour recevoir les messages des clients
while True:
    # Je limite l'effet du timeout uniquement sur le if et non le while
    sock_servr.settimeout(None)

    # Réception du segment
    segment, adresse = sock_servr.recvfrom(1029)

    # Extraction des informations du segment
    commande, numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau, checksum, nom_fichier, donnee = struct.unpack(
        format_entete, segment)

    # Nettoyage de la commande
    commande = commande.rstrip(b"\x00")
    commande = commande.decode('utf-8')

    print("Commande reçue: {}".format(commande))  # Affichage de la commande reçue

    # si commande = open localhost ou open 127.0.0.1
    if commande == "open localhost" or commande == "open 127.0.0.1" or commande == "1":
        print("Demande de connection reçue de la part de {}".format(adresse))
        print()
        ProcessusInitiationConnexion(sock_servr)  # Appel de la fonction ProcessusInitiationConnexion
        print()
        print()
        # print("*"*40)

    # si commande = ls
    elif commande == "ls" or commande == "2":
        print()

        numero_ack = numero_seq + 1
        # Creation et envoi du segment ACK
        segment = CreationSegment(b"", numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau,
                                  GenerateurSignatureHash(b"ACK"), b"", b"ACK")
        EnvoiMessageAvecConnexion(sock_servr, segment)  # Envoi du segment ACK
        print("ACK envoyé")
        print()

        print("Execution de la commande <ls>")
        print()
        print(os.listdir("Dossier_Travail"))

        # Recuperation de la liste du contenu du repertoire de fichiers
        données = os.listdir("Dossier_Travail")

        # Conversion de la liste en chaine de caractere
        données = "\n".join(données)

        # Envoi de la liste des fichiers
        données = données.encode('utf-8')
        segment = CreationSegment(b"", numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau,
                                  GenerateurSignatureHash(données), b"", données)
        EnvoiMessageAvecConnexion(sock_servr, segment)  # Envoi de la liste des fichiers
        print()
        print("Liste des fichiers envoyée")
        print()
        print()

    # si commande = get
    elif commande == "get" or commande == "3":
        print()
        numero_ack = numero_seq + 1
        # Creation et envoi du segment ACK
        segment = CreationSegment(b"", numero_seq, numero_ack, b"ACK", fenetrage_srvr, tailleMorçeau,
                                  GenerateurSignatureHash(b"ACK"), b"", b"ACK")
        EnvoiMessageAvecConnexion(sock_servr, segment)  # Envoi du segment ACK
        print("ACK envoyé")
        print()
        print()
        print("Execution de la commande <get>")  # Affichage visuel de l'état du serveur
        print()

        nom_fichier = nom_fichier.rstrip(b"\x00")

        # Decodage du nom du fichier
        nom_fichier = nom_fichier.decode('utf-8')
        print("Nom du fichier demandé: {}".format(nom_fichier))
        print()
        EnvoiFichier(sock_servr, nom_fichier)
        # print(f"fenetrage_clt : {fenetrage_clt}")
        # print()



    # Si commande = bye
    elif commande == "bye" or commande == "4":
        print()

        EnvoiMessageAvecConnexion(sock_servr, segment)  # Envoi du segment ACK
        print("ACK envoyé")

        sock_servr.close()  # Fermeture du socket
        # print("socket")                  # Affichage visuel de l'état du serveur
        print("Connexion au serveur terminé")  # Affichage visuel de l'état du serveur
        break

    # Erreur d'entrée
    else:
        print()
        print("Commande non reconnue")
        print()
        continue






