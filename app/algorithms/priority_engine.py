from dataclasses import dataclass
from datetime import date
from typing import Tuple,Optional 
@dataclass(frozen = True)
class Weights:
    u: float = 0.40
    i: float = 0.35
    e: float = 0.10
    b: float = 0.15
    def __post_init__(self):
        total = self.u + self.i + self.e + self.b
        if abs(total - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1.0, but got sum = {}".format(total))
@dataclass(frozen = True)
class FactorBreakdown:
     urgency: float
     importance: float
     effort: float
     blocking: float    
def calc_task_score(
        due_date: date,
        importance: int,
        effort: int,
        open_dep_count:int,
        today : date,
        horizon : int = 14,
        weights: Optional[Weights] = None)->Tuple[float, FactorBreakdown]:
        if weights is None:
         weights = Weights()
        d = (due_date - today).days
        if d<0 :
            u = 1.0
        elif d>=horizon:
            u = 0.0
        else:
            u = 1.0-(d/horizon)
        imp = max(1,min(5,importance))
        i = (imp-1)/4.0
        
        eff = max(1,min(5,effort))
        e= (5.0-eff)/4.0
        b = min(1.0,max(0,open_dep_count)/3.0)
        t_score = 100.0*(weights.u*u + weights.i*i + weights.e*e + weights.b*b)
        score = round(t_score,2)
        breakdown = FactorBreakdown(urgency=round(u,3), importance=round(i,3), effort=round(e,3), blocking=round(b,3))
        return score, breakdown
def normalize_weights(w_u: float, w_i: float, w_e: float, w_b: float) -> Weights:
    total = w_u + w_i + w_e + w_b
    if total <= 0 :
        return Weights()
    u= round(w_u/total,4)
    i= round(w_i/total,4)
    e= round(w_e/total,4)
    b= round(1.0 - (u+i+e),4)
    return Weights(u=u, i=i, e=e, b=b) 