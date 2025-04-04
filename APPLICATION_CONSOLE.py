
import socket
import struct
from hashlib import sha1
import random
import os


# Creation du socket client

# Definition des parametres de connexion
hote, port = ('localhost', 2213)

# Creation du socket de type SOCK_DGRAM
sock_client1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Definition des parametres de connexion
address_serveur = ('localhost', 2212)

# Liaison du socket à une adresse IP et un port
sock_client1.bind((hote, port))

#####################################################
               #CONFIGURATIONS

#Nombre d'essais d'envoi de segment
ESSAIES_MAX = 5

#Delai d'attente maximal avant de renvoyer le segment
DELAI_MAX = 3

#Fiabilité du reseau
FIABILITE = round(random.choice([0.95, 1.0]),2)   #remplacer par 1.0 pour simuler un reseau fiable
print(f"Fiabilité du reseau: {FIABILITE}")
print()

#Parametres de l'entête du segment

#Commande
commande = b""
#Numero de sequence
numero_seq = 0   
#Numero d'acquittement
numero_ack = 0
#Drapeau/code de controle
drapeau = b""
#Taille maximal du segment/Maximum segment size
tailleMorçeau = 745 #random.randint(274,280)
#Taille de la fenetre du client
fenetrage =  random.randint(65486,65536)     #tailleMorçeau * 239  #65486

#fenetrage serveur
fenetrage_srvr = 0

checksum = b""
nom_fichier = b""
donnee = b""


#Definition du parametre format de struct.pack
# network byte order numero_seq(4 octets), numero_ack(4 octets), drapeau(3 octets), tailleMorçeau(4 octets), checksum(40 octets), nom_fichier(15 octets), donnee({tailleMorceau} octets)
format_entete = f"!5s I I 3s I I 40s 15s 950s"     


########################################################################################


#Definition de la fonction de creation de segment
def CreationSegment(commande,numero_seq, numero_ack, drapeau, fenetrage, tailleMorçeau, checksum, nom_fichier, donnee):

    #Empaquetage des donnèes du segment
    segment = struct.pack(format_entete, commande, numero_seq, numero_ack, drapeau, fenetrage, tailleMorçeau, checksum, nom_fichier, donnee)
    return segment

######################################################################################


#Definition de la fonction d'envoi de message avec gestion d'erreur
def EnvoiMessage(socket, message, adresse):

    #si le reseau est fiable, on envoie le message 
    if FIABILITE == 1.0:
        # Envoi du message
        try:
            socket.sendto(message, adresse)    # Envoi du message
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
    # Affichage visuel de l'erreur

######################################################################################


#Definition de la fonction de reception de message avec gestion d'erreur
def ReceptionMessage(socket):
    socket.settimeout(DELAI_MAX)    # Delai d'attente maximal pour la reception d'un segment
    try:
        données, adresse = socket.recvfrom(1029)    # Reception du message
        return données

    except socket.timeout:
        print("Delai d'attente depassé")    # Affichage visuel de l'erreur

    except OSError:
        print("Taille du message trop grande")

    except:
        print(f"Erreur inconnue lors de la reception du message")    # Affichage visuel de l'erreur


    
########################################################################################



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


######################################################################################


# Fonction pour l'initiation de la connexion (processus de Three-way handshake)
def ProcessusPoigneDeMain(socket):

    #Pour le passage par reference
    global tailleMorçeau,fenetrage_srvr,fenetrage
    
    print()
    print("********* Processus de poignée de main coté client **************")

    # Création du segment SYN
    segment = CreationSegment(b"",0,0,b"SYN",fenetrage,tailleMorçeau,signature_SYN,b"",b"SYN")
    print()    
    print()
    # Envoi du SYN
    EnvoiMessage(socket, segment, address_serveur)
    print("SYN envoyé")
    print()
    print()

    # Réception du SYN-ACK
    données, adresse = socket.recvfrom(1029)
    
     # Extraction des informations du segment
    commande,numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau1, checksum, nom_fichier, donnee = struct.unpack(format_entete, données)

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
        print("MSS : {}".format(tailleMorçeau1+74)) 
        print()

        #Logique de négociation
        if tailleMorçeau1 < tailleMorçeau:
            tailleMorçeau = tailleMorçeau1  

        #Creation et envoi du segment ACK / Finalisation  de la connexion
        segment = CreationSegment(b"",1, 1, b"ACK", fenetrage, tailleMorçeau, signature_ACK, b"", b"ACK")
        EnvoiMessage(socket, segment, address_serveur)
        print("ACK envoyé")
        print()
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
    print()
    print(f'''        *** Parametres negocié: ***
            Taille_morceau : {tailleMorçeau} 
            Fenetrage_client : {fenetrage}
            Fenetrage_serveur : {fenetrage_srvr}''')
    print()


######################################################################################


#Fonction pour la reception des données
def ReceptionDonnees(socket,nom_fichier_reçu):

    global format_entete

    print()
    print ("Reception des données")
    print()

    with open (nom_fichier_reçu, "wb") as fichier_reçu:
        while True:
            données = socket.recv(1024)
            commande,numero_seq, numero_ack, drapeau, fenetrage1, mss1, checksum, nom_fichier, donnees = struct.unpack(format_entete, données)
            donnée = donnees.rstrip(b"\x00")
            drapeau = drapeau.decode()

            #Verificatio de la fin du fichier
            if drapeau == "FIN":
                print("FIN du fichier reçu")
                break
            fichier_reçu.write(donnée)
    print()
    print("Fichier reçu avec success")





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

    # Si la commande est "bye" ou "4", on ferme la connexion
    if commande == "bye" or commande == "4":

         # Envoi de la commande
        sock_client1.send(commande.encode())   
        sock_client1.close()    # Fermeture du socket
        print("Connexion fermée")    # Affichage visuel de la connexion fermée
        break

    # Si la commande est "ls" ou "2", on affiche la liste des fichiers disponibles
    if commande == "ls" or commande == "2":
        sock_client1.send(commande.encode())
        
        # Reception des données
        données = sock_client1.recv(1024).decode('utf-8')
        print()
        print("****** Liste des fichiers disponibles ******")
        print()
        print(données)
        print()
        print()

    # Si la commande est "open localhost" ou "open
    elif commande == "open localhost" or commande == "open 127.0.0.1" or commande == "1":
        sock_client1.sendto(commande.encode(), address_serveur)    # Envoi de la commande
        ProcessusPoigneDeMain(sock_client1)        # Appel de la fonction ProcessusPoigneDeMain



    elif commande == "get" or commande == "3":
        nom_fichier = input("Entrez le nom du fichier à télécharger: ")
        print() 
        sock_client1.send(commande.encode())    # Envoi de la commande

        # Envoi du nom du fichier à télécharger
        sock_client1.send(nom_fichier.encode())
        print()
        print("Nom du fichier voulu envoyé")

        # Je modifie le nom du fichier à la reception pour eviter les conflits d'ecriture (le fichier source étant dans le meme repertoire)
        nom, extension = os.path.splitext(nom_fichier)
        fichier_reçu = f"{nom}_reçu{extension}"
        print()
        ReceptionDonnees(sock_client1,fichier_reçu)
        print()

        # Reception des données


    else:
        print("Commande inconnue")
        print()
        continue

