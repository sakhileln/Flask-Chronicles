"""
This module provides utility functions for integrating models with an Elasticsearch index.
It includes functions for adding, removing, and querying indexed documents.
"""

from flask import current_app

def add_to_index(index, model):
    """
    Adds a model instance to the specified Elasticsearch index.

    :param index: The name of the Elasticsearch index.
    :param model: The model instance to index, which must have a __searchable__ attribute.
    """
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, document=payload)

def remove_from_index(index, model):
    """
    Removes a model instance from the specified Elasticsearch index.

    :param index: The name of the Elasticsearch index.
    :param model: The model instance to remove.
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    """
    Performs a search query on the specified Elasticsearch index.

    :param index: The name of the Elasticsearch index.
    :param query: The search query string.
    :param page: The current page number for pagination.
    :param per_page: The number of results per page.
    :return: A tuple containing a list of document IDs and the total number of matching documents.
    """
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        query={'multi_match': {'query': query, 'fields': ['*']}},
        from_=(page - 1) * per_page,
        size=per_page)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
