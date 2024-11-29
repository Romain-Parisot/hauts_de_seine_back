from enum import Enum

class Status(str, Enum):
  donationRequest = "requete de dons"
  receivedTownHall = "reçu en mairie"
  receivedAsso = "receptione dans l'asso"
  reconditioning = "en reconditionement"
  reconditionedAwaitingRecipient = "reconditioné en attende de receveur"
  delivered = "délivrer au receveur"
  