
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
FIABILITE = 1#round(random.choice([0.95, 1.0]),2)   #remplacer par 1.0 pour simuler un reseau fiable
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
tailleMorçeau = 730 #random.randint(274,280)
#Taille de la fenetre du client
fenetrage =  random.randint(65486,65536)     #tailleMorçeau * 239  #65486

#fenetrage serveur
fenetrage_srvr = 0

checksum = b""
nom_fichier = b""
donnee = b""


#Definition du parametre format de struct.pack
# network byte order numero_seq(4 octets), numero_ack(4 octets), drapeau(3 octets), tailleMorçeau(4 octets), checksum(40 octets), nom_fichier(15 octets), donnee({tailleMorceau} octets)
format_entete = f"!25s I I 3s I I 40s 25s 920s"     


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
    

######################################################################################


#Definition de la fonction d'envoi de message avec connexion établie
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


########################################################################################

#Calcul et assignation des signatures de quelques parametres
signature_SYN = GenerateurSignatureHash(b"SYN")
signature_ACK = GenerateurSignatureHash(b"ACK")
signature_SYN_ACK = GenerateurSignatureHash(b"SYN-ACK")


######################################################################################


# Fonction pour l'initiation de la connexion (processus de Three-way handshake)
def ProcessusPoigneDeMain(socket):

    #Pour le passage par reference
    global tailleMorçeau,fenetrage_srvr,fenetrage,numero_seq,numero_ack
    
    print()
    print("********* Processus de poignée de main coté client **************")

    # Création du segment SYN
    segment = CreationSegment(b"",numero_seq,numero_ack,b"SYN",fenetrage,tailleMorçeau,signature_SYN,b"",b"SYN")

    print()    
    print()
    # Envoi du SYN
    EnvoiMessage(socket, segment, address_serveur)
    print("SYN envoyé")
    print()
    print()

    #On attends une confirmation de reception(SYN-ACK) pendant 3 secondes
    socket.settimeout(DELAI_MAX)
    try:
        # Réception du SYN-ACK
        données, adresse = socket.recvfrom(1029)

    # Si le segment n'est pas reçu dans le delai imparti, on renvoie le segment SYN a 5 reprises    
    except socket.timeout:
        print("Delai d'attente depassé")
        print()
        print("Reexpedition du segment SYN ")
        print()

        for index in range(ESSAIES_MAX):
            EnvoiMessage(socket, segment, address_serveur)
            print("Tentive de renvoi du segment SYN n° {}".format(index+1))
            print()
            socket.settimeout(DELAI_MAX)
            try:
                données, adresse = socket.recvfrom(1029)
                break
            except socket.timeout:
                if index == ESSAIES_MAX:
                    print("Echec de la poignée de main")
                    print()
                    print("Connexion terminée")
                    socket.close()
                    return
                
                print("Delai d'attente depassé")
                print()
                print("Reexpedition du segment SYN ")
                continue
              

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
        print("Numero de sequence reçu: {}".format(numero_seq))
        print("Numero d'acquittement reçu: {}".format(numero_ack))
        print("Drapeau reçu: {}".format(drapeau))
        print("Fenetrage_serveur reçu: {}".format(fenetrage1))
        print("MSS reçu: {}".format(tailleMorçeau1+74)) 
        print()

        #Logique de négociation
        if tailleMorçeau1 < tailleMorçeau:
                tailleMorçeau = tailleMorçeau1 

        numero_seq = 1
        numero_ack = 1 

        #Creation et envoi du segment ACK / Finalisation  de la connexion
        segment = CreationSegment(b"",numero_seq, numero_ack, b"ACK", fenetrage, tailleMorçeau, signature_ACK, b"", b"ACK")
        EnvoiMessage(socket, segment, address_serveur)
        print("ACK envoyé")
        print()


        print()
      
    #Sinon il y'a affichage d'un message d'erreur
    else:
        print("SYN-ACK reçu corrompu")
        print()
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
            données = socket.recv(1029)
            commande,numero_seq, numero_ack, drapeau, fenetrage1, mss1, checksum, nom_fichier, donnees = struct.unpack(format_entete, données)
            donnée = donnees.rstrip(b"\x00")
            drapeau = drapeau.decode()

            #Verification de la fin du fichier
            if drapeau == "FIN":
                print("FIN du fichier")
                break
            fichier_reçu.write(donnée)
    print()
    print("Fichier reçu avec success")


#################################################################################

                                   
                                    #PROGRAMME PRINCIPAL


# Boucle infinie pour l'envoi des commandes
while True:
    print()
    print("*"*50)
    print()
    print("Que voulez vous faire?")
    print()
    print("Les commandes suivantes sont disponibles:")
    print()
    print("1. open localhost")
    print("2. ls")
    print("3. get")
    print("4. bye")
    print()
    print("Veuillez entrer le chiffre correspondant a la commande")
    print()
    commande = input("Commande: ")

    #Conversion de la commande en bytes
    commande = commande.encode('utf-8')
    print()

    numero_seq = numero_ack + 1
    # Creation du segment
    segment = CreationSegment(commande, numero_seq, numero_ack, b"", fenetrage, tailleMorçeau, b"", b"", b"")


    # Si la commande est "bye" ou "4", on ferme la connexion
    if commande == b"bye" or commande == b"4":

         # Envoi de la commande
        segment = CreationSegment(b"bye", numero_seq, numero_ack, b"", fenetrage, tailleMorçeau, b"", b"", b"")
        EnvoiMessageAvecConnexion(sock_client1, segment)
        print("Commande bye envoyée")
        print()
        
        sock_client1.settimeout(DELAI_MAX)
        try:
            # Réception de la confirmation de reception
            données = sock_client1.recv(1029)
            print("Commande bye reçue")
            print()
        except socket.timeout:
            print("Delai d'attente depassé")
            print()
            print("Reexpedition de la commande bye")
            print()
            for index in range(ESSAIES_MAX):
                EnvoiMessageAvecConnexion(socket, segment)
                print("Tentative de renvoi de la commande bye n° {}".format(index+1))
                print()
                sock_client1.settimeout(DELAI_MAX)
                try:
                    données, adresse = sock_client1.recvfrom(1029)
                    break
                except socket.timeout:
                    if index == ESSAIES_MAX - 1:
                        print("Echec de la connexion")
                        print()
                        sock_client1.close()
                        print("Connexion terminée")
                    
                    print("Delai d'attente depassé")
                    print()
                    continue

        sock_client1.close()    # Fermeture du socket
        print("Connexion fermée")    # Affichage visuel de la connexion fermée
        break

    # Si la commande est "ls" ou "2", on affiche la liste des fichiers disponibles
    elif commande == b"ls" or commande == b"2":

        # Envoi de la commande
        EnvoiMessageAvecConnexion(sock_client1, segment)
        print("Commande ls envoyée")

        #Attente de la confirmation de reception
        sock_client1.settimeout(DELAI_MAX)

        try:
            # Réception de la liste des fichiers
            données = sock_client1.recv(1029)
            # Extraction des informations du segment
            commande,numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau1, checksum, nom_fichier, donnee = struct.unpack(format_entete, données)

            if signature_ACK == checksum.rstrip(b"\x00"):

                print("commande ls reçue")
                print()
            else:
                print("commande ls corrompue")
                print()
                print("Echec de la reception de la commande ls")
                print()
                sock_client1.close()
                break

        except socket.timeout:
            print("Delai d'attente depassé")
            print()
            print("Reexpedition de la commande ls")
            print()
            for index in range(ESSAIES_MAX):
                EnvoiMessageAvecConnexion(socket, segment)
                print("Tentative de renvoi de la commande ls n° {}".format(index+1))
                print()
                sock_client1.settimeout(DELAI_MAX)
                try:
                    données = sock_client1.recv(1029)
                    # Extraction des informations du segment
                    commande,numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau1, checksum, nom_fichier, donnee = struct.unpack(format_entete, données)

                    break
                except socket.timeout:
                    if index == ESSAIES_MAX - 1:
                        print("Echec de la connexion")
                        print()
                        sock_client1.close()
                        print("Connexion terminée")
                    
                    print("Delai d'attente depassé")
                    print()
                    continue

        
        # Reception des données
        données = sock_client1.recv(1029)
        # Extraction des informations du segment
        commande,numero_seq, numero_ack, drapeau, fenetrage1, tailleMorçeau1, checksum, nom_fichier, donnee = struct.unpack(format_entete, données)
        donnee = donnee.rstrip(b"\x00")
        donnee = donnee.decode('utf-8')
        print()
        print("****** Liste des fichiers disponibles ******")
        print()
        print(donnee)
        print()
        print() 

    # Si la commande est "open localhost" ou "open
    elif commande == b"open localhost" or commande == b"open 127.0.0.1" or commande == b"1":

        # Envoi de la commande
        EnvoiMessage(sock_client1, segment, address_serveur)
        print("Commande open localhost envoyée")
        print()
        print()
        ProcessusPoigneDeMain(sock_client1)        # Appel de la fonction ProcessusPoigneDeMain



    elif commande == b"get" or commande == b"3":
        nom_fichier = input("Entrez le nom du fichier à télécharger: ")
        print()

        commande = b"get"
        nom_fichier = nom_fichier.encode('utf-8')

        numero_seq = numero_ack
        # Creation du segment
        segment = CreationSegment(commande, numero_seq, numero_ack, b"", fenetrage, tailleMorçeau, b"", nom_fichier, b"")
        
        # Envoi de la commande
        EnvoiMessageAvecConnexion(sock_client1, segment)
        print("Commande get envoyée pour le fichier {}".format(nom_fichier.decode('utf-8')))
        print()

        sock_client1.settimeout(DELAI_MAX)
        try:
            # Réception de la confirmation de reception
            données = sock_client1.recv(1029)
            print("Commande get reçue")
            print()
        except socket.timeout:
            print("Delai d'attente depassé")
            print()
            print("Reexpedition de la commande get")
            print()
            for index in range(ESSAIES_MAX):
                EnvoiMessageAvecConnexion(socket, segment)
                print("Tentative de renvoi de la commande get n° {}".format(index+1))
                print()
                sock_client1.settimeout(DELAI_MAX)
                try:
                    données, adresse = socket.recvfrom(1029)
                    break
                except sock_client1.timeout:
                    if index == ESSAIES_MAX - 1:
                        print("Echec de la connexion")
                        print()
                        sock_client1.close()
                        print("Connexion terminée")
                    
                    print("Delai d'attente depassé")
                    print()
                    print("Tentative de reexpedition du segment SYN-ACK numero {}".format(index+1))
                    continue


        # Je modifie le nom du fichier à la reception pour eviter les conflits d'ecriture (le fichier source étant dans le meme repertoire)
        nom, extension = os.path.splitext(nom_fichier)
        nom = nom.decode('utf-8')
        extension = extension.decode('utf-8')
        print()
       # print(f"Nom du fichier: {nom}")
        #print(f"Extension du fichier: {extension}")
        fichier_reçu = f"{nom}_reçu{extension}"
        print()
        print(f"Nom du fichier reçu: {fichier_reçu}")
        print()
        ReceptionDonnees(sock_client1,fichier_reçu)
        print()

        # Reception des données


    else:
        print("Commande inconnue")
        print()
        continue

