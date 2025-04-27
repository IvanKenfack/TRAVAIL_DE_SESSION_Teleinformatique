import struct
import os
from tqdm import tqdm
import hashlib
import time
import random
import sys


format_entete = f"!25s I I 3s I I 40s 25s 920s"
fenetrage_clt = 0
fenetrage_srvr = 0
tailleMorçeau = 920
numero_ack = 0
numero_seq = 0


# Definition de la fonction de creation de segment
def CreationSegment(commande, numero_seq, numero_ack, drapeau, fenetrage, tailleMorçeau, checksum, nom_fichier, donnee):
    # Empaquetage des donnèes du segment
    segment = struct.pack(format_entete, commande, numero_seq, numero_ack, drapeau, fenetrage, tailleMorçeau, checksum,
                          nom_fichier, donnee)
    return segment


# Definition du generateur du checksum/hash avec la fonction de hachage sha1
def GenerateurSignatureHash(donnee):
    # initialisation de l'objet sha1
    objet_sha1 = sha1()

    # mise a jour de l'objet sha1 avec les donnees
    objet_sha1.update(donnee)

    # generation de la signature
    signature = objet_sha1.digest()

    # retourne la signature
    return signature




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

    # Fonction pour la reception des données
def ReceptionDonnees(socket, nom_fichier_reçu):
    global format_entete

    print()
    print("Reception des données")
    print()

    with open(nom_fichier_reçu, "wb") as fichier_reçu:
        while True:
            données = socket.recv(1029)
            commande, numero_seq, numero_ack, drapeau, fenetrage1, mss1, checksum, nom_fichier, donnees = struct.unpack(
                format_entete, données)
            donnée = donnees[:mss1]
            drapeau = drapeau.decode()

            # Verification de la fin du fichier
            if drapeau == "FIN":
                print("FIN du fichier")
                break
            fichier_reçu.write(donnée)
    print()
    print("Fichier reçu avec success")

