
import socket

hote, port = ('localhost', 2212)     # Même couple hote/port que celui du serveur
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Connexion au serveur avec mechanisme de gestion d'erreur

try:
    socket.connect((hote, port))
    print("Le client est connecté !")
except:
    print("La connexion au serveur à échoué !")
finally:
    socket.close()      # Fermeture du socket

