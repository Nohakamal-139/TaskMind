from typing import Dict,List,Optional,Tuple
def detect_cycle(task_a: int,dep_b:int,deps:Dict[int, List[int]])-> Optional[List[int]]:
    if task_a == dep_b:
        return [task_a,task_a]
    stack: List[List[int]]= [[dep_b]]
    seen = set()
    while stack:
        path = stack.pop()
        node = path[-1]
        if node  == task_a:
            return [task_a]+path
        if node not in seen:
            seen.add(node)
            for pre in deps.get(node,[]):
                if pre not in seen or pre == task_a:
                    stack.append(path+[pre])
    return None
def create(task_a: int, depends_on_b: int, deps: Dict[int, List[int]])->bool:
    return detect_cycle(task_a, depends_on_b, deps) is not None


