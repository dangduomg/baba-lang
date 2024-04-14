from typing import List
from dataclasses import dataclass


@dataclass
class Cell:
    value: object

class State:
    scopes: List[dict]
    
    def __init__(self):
        self.scopes = [{}]
        
    def copy(self) -> 'State':
        new_state = State()
        new_state.scopes = self.scopes[:]
        return new_state
        
    def new_scope(self) -> None:
        self.scopes.append({})
        
    def exit_scope(self) -> None:
        self.scopes.pop()
        
    def resolve_var(self, name: str) -> Cell:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError(f'Can\'t find variable {name}!')
    
    def get_var(self, name: str) -> object:
        return self.resolve_var(name).value
    
    def new_var(self, name: str, value: object) -> None:
        self.scopes[-1][name] = Cell(value)
        
    def set_var(self, name: str, value: object) -> None:
        self.resolve_var(name).value = value