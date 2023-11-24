from components.database.DDBConnector import DDBConnector
from components.repository.Repository import Repository
from components.repository.User import User

class DDBRepository(Repository):

    def __init__(self) -> None:
        self.ddb_connector =  DDBConnector('', '') #TODO: gather them from  env variables?