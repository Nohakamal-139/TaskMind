from datetime import date
from typing import List, Dict, Tuple, Optional
from app.database.connection import get_connection
from app.database.repositories import TaskRepository, ProjectRepository
from app.algorithms.cycle_detector import create, detect_cycle


class TaskService:
    
    def __init__(self):
        self.conn = get_connection()
        self.task_repo = TaskRepository()
        self.project_repo = ProjectRepository()

    def get_all_projects(self) -> List[str]:
        projects = self.project_repo.list_all(self.conn) 
        return [p.name for p in projects]

    def get_all_tasks(self) -> List[dict]:
        tasks = self.task_repo.list_all(self.conn)
        result = []
        task_status_map = {t.id: t.status for t in tasks}

        for t in tasks:
            deps = self.task_repo.get_dependencies(t.id, self.conn) if hasattr(self.task_repo, 'get_dependencies') else []
            is_blocked = any(task_status_map.get(dep_id) != "DONE" for dep_id in deps)
            
            result.append({
                "id": t.id,
                "name": t.title,
                "project": self.project_repo.get_by_id(t.project_id, self.conn).name if hasattr(self.project_repo, 'get_by_id') and t.project_id else "No project",
                "status": t.status,
                "priority": "Medium",
                "importance": getattr(t, 'importance', 3),
                "effort": getattr(t, 'effort', 3),
                "due": t.due_date.format() if hasattr(t, 'due_date') and t.due_date else "",
                "dependencies": deps,
                "is_blocked": is_blocked
            })
        return result

    def add_task_with_cycle_check(
        self, title: str, project_name: str, due_date: date,
        importance: int, effort: int, dependencies: List[int]
    ) -> Tuple[bool, Optional[str]]:
        
        all_deps = self.task_repo.get_all_dependency_pairs() if hasattr(self.task_repo, 'get_all_dependency_pairs') else []
        deps_map: Dict[int, List[int]] = {}
        for a, b in all_deps:
            deps_map.setdefault(a, []).append(b)

        temp_id = 999999
        for dep_id in dependencies:
            path = detect_cycle(temp_id, dep_id, deps_map)
            if path:
                return False, f"Cycle detected: {' -> '.join(map(str, path))}"

        project = self.project_repo.get_by_name(project_name, self.conn) if hasattr(self.project_repo, 'get_by_name') else None
        project_id = project.id if project else None

        task_id = self.task_repo.create(
            project_id=project_id,
            title=title,
            due_date=due_date,
            importance=importance,
            effort=effort,
            status="TODO"
        )

        if hasattr(self.task_repo, 'add_dependency'):
            for dep_id in dependencies:
                self.task_repo.add_dependency(task_id, dep_id)

        return True, None