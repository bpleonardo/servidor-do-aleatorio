from typing import Dict, Any, Optional, AsyncIterator
from collections import deque

from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


NoResults = -999


class Document:
    def __init__(self, collection, data: Dict[str, Any]):
        self.collection: Collection = collection
        self.data = data or {}

    def __iter__(self):
        return iter(self.data.items())

    def __getattr__(self, attr: str):
        from_data = self.data.get(attr)
        if from_data:
            return from_data
        raise AttributeError(f"'Document' object has no attribute '{attr}'")

    def update(self, **update) -> None:
        """
        Atualiza os atributos do documento.

        Utilize este método no lugar de setattr.
        """
        self.data.update(update)

    async def update_and_sync(self, update: Dict[str, Dict[str, Any]]):
        updated = await self.collection.update(self._id, update)
        self.data = updated.data.copy()
        return self

    async def sync(self) -> None:
        """Sincroniza as alterações com a database."""
        await self.collection.update(self._id, {'$set': self.data})

    async def delete(self) -> None:
        """Deleta o documento da database."""
        await self.collection.delete(self._id)
        self.data = {}


class DBLRUCache:
    """
    Minha própria implementação de LRU cache feita para funcionar com esta database.
    Foi bastante modificado.
    """
    __slots__ = ('max_size', '__container', '__map')

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.__container = deque()  # deque de (id, documento)
        self.__map = dict()

    def reallocate(self) -> None:
        """
        Isso deixará o _map com o id do documento como index e o
        documento como valor.
        """
        self.__map = dict()
        if len(self.__container) > 0:
            for key, value in enumerate(self.__container):
                self.__map[value[0]] = key

    def get(self, id_: str, doc: Document = NoResults) -> Optional[Document]:
        """
        Isso retornará o valor do cache, se existir, e atualizar as
        posições.
        Caso não exista, irá executar insert(id_, fallback) e o retornar.
        """
        if id_ in self.__map:
            val = self.__container[self.__map[id_]]

            self.__container.remove(val)
            self.__container.appendleft(val)
            self.reallocate()

            return val[1]

        if doc is not NoResults:
            return self.insert(id_, doc)

        return NoResults

    def remove(self, id_: str) -> None:
        """Isso irá remover o id do cache."""
        if id_ in self.__map:
            del self.__container[self.__map[id_]]
            del self.__map[id_]
            self.reallocate()

    def _insert(self, id_, doc):
        self.__container.appendleft((id_, doc))
        self.reallocate()

    def insert(self, id_: str, doc: Document) -> Document:
        """Isso irá adicionar o documento ou atualizar seu uso."""
        if id_ in self.__map:
            self.get(id_)
        else:
            if len(self.__map) == self.max_size:
                self.__container.pop()
            self._insert(id_, doc)
        return doc


class Collection:
    __slots__ = ('collection', 'template', '__cache')

    def __init__(self, collection: AsyncIOMotorCollection, template=None):
        if not template:
            template = {}
        self.collection: AsyncIOMotorCollection = collection
        self.template = template
        self.__cache = DBLRUCache(100)

    async def new(self, id_: str) -> Document:
        id_ = str(id_)
        template = self.template.copy()
        template.update({'_id': id_})

        await self.collection.insert_one(template)
        return self.__cache.insert(id_, Document(self, template))

    async def delete(self, id_: str):
        id_ = str(id_)
        await self.collection.delete_one({'_id': id_})
        self.__cache.remove(id_)
        self.__cache.insert(id_, None)

    async def find(self, id_: str) -> Document:
        id_ = str(id_)

        from_cache = self.__cache.get(id_)
        if from_cache is not NoResults:
            return from_cache

        doc = await self.collection.find_one({'_id': id_})

        if doc is None:
            return self.__cache.insert(id_, None)

        return self.__cache.insert(id_, Document(self, doc))

    async def update(self,
                     id_: str,
                     update: Dict[str, Dict[str, Any]]) -> Document:
        id_ = str(id_)

        updated = await self.collection.find_one_and_update(
            {'_id': id_},
            update,
            return_document=ReturnDocument.AFTER
        )
        if not updated:
            await self.new(id_)
            return await self.update(id_, update)

        self.__cache.remove(id_)

        return self.__cache.insert(id_, Document(self, updated))

    async def all(self) -> AsyncIterator[Document]:
        cursor = self.collection.find({})
        async for doc in cursor:
            yield Document(self, doc)


class Database:
    __slots__ = ('client', 'db')

    def __init__(self, name: str, *args, **kwargs):
        self.client = AsyncIOMotorClient(*args, **kwargs)
        self.db = self.client[name]

    def get_collection(self,
                       name: str,
                       template: Dict[str, Any] = None) -> Collection:
        return Collection(self.db[name], template)
