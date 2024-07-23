from app.core.vectorstore.customer_milvus_client import CustomerMilvusClient
if __name__ == '__main__':
    CustomerMilvusClient().delete_collection()