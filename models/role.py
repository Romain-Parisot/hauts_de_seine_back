from enum import Enum

class Role(str, Enum):
    mairie = "mairie"
    particulier = "particulier"
    association = "association"
