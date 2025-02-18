
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


ProcessusPoigneDeMain(sock_client1)        # Appel de la fonction ProcessusPoigneDeMain
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

sock_client1.close()      # Fermeture du socket

