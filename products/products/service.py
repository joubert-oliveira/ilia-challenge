import logging

from nameko.events import event_handler
from nameko.rpc import rpc
from nameko.exceptions import RpcError

from products import dependencies, schemas


logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()

    @rpc
    def get(self, product_id):
        product = self.storage.get(product_id)
        return schemas.Product().dump(product).data

    @rpc
    def list(self):
        products = self.storage.list()
        return schemas.Product(many=True).dump(products).data

    @rpc
    def create(self, product):
        product = schemas.Product(strict=True).load(product).data
        self.storage.create(product)

    @rpc
    def delete(self, product_id):
        try:
        product = self.storage.get(product_id)
        if product:
            self.storage.delete(product_id)
            return {"message": "Product deleted successfully", "status": "success"}
        else:
            raise RpcError("Product not found", 404)
        except Exception as e:
            raise RpcError(f"Failed to delete product: {str(e)}", 500)

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])
