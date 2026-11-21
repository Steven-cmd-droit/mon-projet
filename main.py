# TaskFlow CLI

Un gestionnaire de tâches complet en ligne de commande écrit en Python, permettant d'organiser ses projets, définir des priorités et sauvegarder automatiquement les données au format JSON.

## Fonctionnalités
- Ajout, modification et suppression de tâches
- Gestion des niveaux de priorité (Haute, Moyenne, Basse)
- Filtrage par statut (En cours / Terminées)
- Persistance automatique des données dans un fichier local `tasks.json`
- Statistiques de productivité

## Installation et utilisation
```bash
python main.py

3. Clique sur le bouton vert **Commit changes...** en haut à droite, puis valide dans la fenêtre qui s'ouvre.

---

### Étape 2 : Créer le fichier de code `main.py`
1. Reviens sur la page principale de ton dépôt, clique sur le bouton **`Add file`** puis **`Create new file`**.
2. Dans la case **Name your file...**, écris `main.py`.
3. Colle le code complet ci-dessous dans la zone de texte :

```python
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Task:
    """Représente une tâche individuelle avec ses métadonnées."""

    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = "Moyenne",
        completed: bool = False,
        created_at: Optional[str] = None,
        task_id: Optional[int] = None,
    ):
        self.id = task_id or int(datetime.now().timestamp() * 1000)
        self.title = title
        self.description = description
        self.priority = priority if priority in ["Haute", "Moyenne", "Basse"] else "Moyenne"
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "Moyenne"),
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            task_id=data.get("id"),
        )


class TaskManager:
    """Gère la collection de tâches et la sauvegarde sur disque."""

    def __init__(self, storage_file: str = "tasks.json"):
        self.storage_file = storage_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self) -> None:
        if not os.path.exists(self.storage_file):
            self.tasks = []
            return
        try:
            with open(self.storage_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.tasks = [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError):
            print("Erreur lors de la lecture du fichier de sauvegarde. Initialisation à vide.")
            self.tasks = []

    def save_tasks(self) -> None:
        try:
            with open(self.storage_file, "w", encoding="utf-8") as file:
                json.dump([task.to_dict() for task in self.tasks], file, indent=4, ensure_ascii=False)
        except IOError as error:
            print(f"Impossible de sauvegarder les tâches : {error}")

    def add_task(self, title: str, description: str, priority: str) -> Task:
        new_task = Task(title=title, description=description, priority=priority)
        self.tasks.append(new_task)
        self.save_tasks()
        return new_task

    def complete_task(self, index: int) -> bool:
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True
            self.save_tasks()
            return True
        return False

    def delete_task(self, index: int) -> bool:
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save_tasks()
            return True
        return False

    def get_statistics(self) -> Dict[str, int]:
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        pending = total - completed
        high_priority = sum(1 for task in self.tasks if task.priority == "Haute" and not task.completed)
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority": high_priority,
        }


def display_menu() -> None:
    print("\n" + "=" * 45)
    print("         TASKFLOW CLI - GESTIONNAIRE")
    print("=" * 45)
    print("1. Afficher toutes les tâches")
    print("2. Ajouter une nouvelle tâche")
    print("3. Marquer une tâche comme terminée")
    print("4. Supprimer une tâche")
    print("5. Voir les statistiques")
    print("6. Quitter")
    print("=" * 45)


def main() -> None:
    manager = TaskManager()

    while True:
        display_menu()
        choice = input("Choisissez une option (1-6) : ").strip()

        if choice == "1":
            if not manager.tasks:
                print("\nAucune tâche enregistrée pour le moment.")
            else:
                print("\nListe des tâches :")
                for idx, task in enumerate(manager.tasks, start=1):
                    status = "✔" if task.completed else "✘"
                    print(f"[{idx}] [{status}] {task.title} (Priorité : {task.priority})")
                    if task.description:
                        print(f"    Description : {task.description}")

        elif choice == "2":
            title = input("Titre de la tâche : ").strip()
            if not title:
                print("Le titre ne peut pas être vide.")
                continue
            description = input("Description (optionnelle) : ").strip()
            priority = input("Priorité (Haute / Moyenne / Basse) : ").strip().capitalize()
            task = manager.add_task(title, description, priority)
            print(f"Tâche '{task.title}' ajoutée avec succès.")

        elif choice == "3":
            try:
                idx = int(input("Numéro de la tâche à terminer : ")) - 1
                if manager.complete_task(idx):
                    print("Tâche marquée comme terminée.")
                else:
                    print("Numéro de tâche invalide.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")

        elif choice == "4":
            try:
                idx = int(input("Numéro de la tâche à supprimer : ")) - 1
                if manager.delete_task(idx):
                    print("Tâche supprimée.")
                else:
                    print("Numéro de tâche invalide.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")

        elif choice == "5":
            stats = manager.get_statistics()
            print("\n--- Statistiques ---")
            print(f"Total des tâches       : {stats['total']}")
            print(f"Tâches terminées       : {stats['completed']}")
            print(f"Tâches en cours        : {stats['pending']}")
            print(f"Priorité haute actives : {stats['high_priority']}")

        elif choice == "6":
            print("Fermeture de TaskFlow CLI. À bientôt !")
            break

        else:
            print("Option invalide, veuillez réessayer.")


if __name__ == "__main__":
    main()
