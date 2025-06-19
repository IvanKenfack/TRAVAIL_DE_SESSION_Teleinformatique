Implémentation d'un service de transfert de fichiers fiable en utilisant les sockets UDP en python 3.13
# INF26207 – Transfert de fichier via Sockets UDP

Travail de session du cours **INF26207 – Téléinformatique**, Hiver 2025, UQAR 
Ce projet consiste à concevoir un protocole simple de transfert de fichiers fiable, basé sur **UDP (avec `socket.socket`)**, en simulant un environnement réseau peu fiable.

## Objectifs

- Maîtriser la communication réseau via les **sockets UDP**.
- Simuler les principes de **TCP (handshake, fenêtrage, accusés de réception)**.
- Gérer la **sérialisation** et le découpage des fichiers en blocs binaires.
- Implémenter un protocole simple, fiable et extensible.

## Technologies et outils

-  **Langage** : Python 3.13
-  **Librairies utilisées** :
  - `socket`, `random`, `os`, `struct`, `hashlib`
  - `tqdm` (pour la barre de progression)
-  Outils : VS Code

## Fonctionnement général

L'application est constituée de deux scripts principaux :

```plaintext 
├── server.py    # Serveur UDP (port 2212)
├── client.py    # Client console
├── config.json  # Fichier de configuration (pour simuler la fiabilité du réseau)
└── README.md
