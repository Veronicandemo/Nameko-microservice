# dependency provider that gives the service read only access to configuration values at runtime
from nameko  import config

# class attribute that is responsible for providing an object that is injected into the  service workers
from nameko.extensions import dependancyProvider

from products.exceptions import NotFound

REDIS_URI_KEY = 'REDIS_URI'

class StorageWrapper:
    """
    Product Storage
    
    A very simple example of a custom Nameko dependency.  Simplified
    implementation of products database based on Redis key value store.
    Handling the product ID increments or keeping sorted sets of product
    names for ordering the products is out of the scope of this example.
    """
    
    NotFound = NotFound
    
    def __init__(self, client):
        self.client = client
    
    def _format_key(self, product_id):
        return f'products:{product_id}'
    
    def _from_hash(self, document):
        return {
            'id': document[b'id'].decode('utf-8'),
            'title': document[b'title'].decode('utf-8'),
            'passenger_capacity': int(document[b'passenger_capacity']),
            'maximum_speed': int(document[b'maximum_speed']),
            'in_stock': int(document[b'in_stock'])
        }
    
    def get(self, product_id):
        product = self.client.hgetall(self._format_key(product_id))
        if not product:
            raise NotFound(f"Product id {product_id} does not exist")
        else:
            return self._from_hash(product)
        
    def list(self):
        keys = self.client.keys(self._format_key('*'))
        for key in keys:
            yield self._from_hash(self.client.hgetall(key))
    
    def create(self, product):
        self.client.hmset(
            self._format_key(product['id']),
            product
        )
        
    def decrement_stock(self, product_id, amount):
        return self.client.hincrby(
            self._format_key(product_id), 'in_stock', -amount)


class Storage(dependancyProvider):
    
    def setup(self):
        self.client = redis.StrictRedis.from_url(config.get(REDIS_URI_KEY))
        
    def get_dependencies(self, worker_ctx):
        return StorageWrapper(self.client)
        
