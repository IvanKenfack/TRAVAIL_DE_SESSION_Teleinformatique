Implémentation d'un service de transfert de fichiers fiable en utilisant les sockets UDP en python 3.10
# INF26207 – Transfert de fichier via Sockets UDP (TP)

Projet individuel ou en binôme – Travail de session du cours **INF26207 – Téléinformatique**, Hiver 2025  
Ce projet consiste à concevoir un protocole simple de transfert de fichiers fiable, basé sur **UDP (avec `socket.socket`)**, en simulant un environnement réseau peu fiable.

## Objectifs

- Maîtriser la communication réseau via les **sockets UDP**.
- Simuler les principes de **TCP (handshake, fenêtrage, accusés de réception)**.
- Gérer la **sérialisation** et le découpage des fichiers en blocs binaires.
- Implémenter un protocole simple, fiable et extensible.

## Technologies et outils

-  **Langage** : Python 3.10+ (ou Rust si précisé)
-  **Librairies autorisées** :
  - `socket`, `random`, `os`, `struct`, `hashlib`
  - `tqdm` (optionnelle – pour les barres de progression)
-  Outils : VS Code recommandé avec plugins de documentation

## Fonctionnement général

L'application est constituée de deux scripts principaux :

```plaintext
├── server.py    # Serveur UDP (port 2212)
├── client.py    # Client console
├── config.json  # Fichier de configuration (ex. fiabilité du réseau)
└── README.md
