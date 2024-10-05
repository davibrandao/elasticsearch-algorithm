from elasticsearch_dsl import Search
from elasticsearch.exceptions import NotFoundError
from .documents import ItemDocument
from .models import Item

class RecommendationService:
    @staticmethod
    def get_recommendations(item_id, limit=5):
        try:
            item = ItemDocument.get(id=item_id)
        except NotFoundError:
            return []
        
        query = {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": f"{item.title} {item.description}",
                        "fields": ["title^3", "description^2", "tags^2", "category"],
                        "type": "best_fields",
                        "tie_breaker": 0.3,
                        "minimum_should_match": "30%"
                    }
                },
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "popularity_score",
                            "factor": 1.2,
                            "modifier": "log1p"
                        }
                    }
                ],
                "boost_mode": "multiply"
            }
        }
        
        try:
            s = RecommendationService.build_search(query, item_id)
            response = s.execute()
            
            recommended_items = []
            for hit in response[:limit]:
                try:
                    recommended_items.append(Item.objects.get(id=hit.meta.id))
                except Item.DoesNotExist:
                    continue
            
            return recommended_items
        except Exception:
            return []

    @staticmethod
    def build_search(query, item_id):
        s = Search(index='items').query(query)
        s = s.exclude("term", id=item_id)
        return s

class ItemService:
    @staticmethod
    def search_items(query, category=None, page=1, per_page=10):
        search = ItemDocument.search()

        if query:
            search = search.query("multi_match", query=query, fields=['title', 'description'])
        
        if category:
            search = search.filter('term', category=category)
        
        # Add aggregation for categories
        search.aggs.bucket('categories', 'terms', field='category')
        
        # Paginate results
        start = (page - 1) * per_page
        search = search[start:start + per_page]

        response = search.execute()
        
        return {
            'items': response,
            'total': response.hits.total.value,
            'category_facets': response.aggregations.categories.buckets
        }

    @staticmethod
    def get_item_by_id(item_id):
        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return None

    @staticmethod
    def create_item(title, description, category):
        item = Item(title=title, description=description, category=category)
        item.save()
        return item

    @staticmethod
    def update_item(item_id, **kwargs):
        try:
            item = Item.objects.get(id=item_id)
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save()
            return item
        except Item.DoesNotExist:
            return None

    @staticmethod
    def delete_item(item_id):
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
            return True
        except Item.DoesNotExist:
            return False