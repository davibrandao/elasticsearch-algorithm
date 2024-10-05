from elasticsearch_dsl import Search
from .documents import ItemDocument

class RecommendationService:
    @staticmethod
    def get_recommendations(item_id, limit=5):
        item = ItemDocument.get(id=item_id)
        
        # Create a multi-match query
        query = {
            "multi_match": {
                "query": f"{item.title} {item.description}",
                "fields": ["title^3", "description^2", "tags^2", "category"],
                "type": "best_fields",
                "tie_breaker": 0.3,
                "minimum_should_match": "30%"
            }
        }
        
        # Create a function score query to boost by popularity
        function_score_query = {
            "function_score": {
                "query": query,
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
        
        # Execute the search
        s = Search(index='items').query(function_score_query)
        s = s.exclude("match", id=item_id)  # Exclude the current item
        response = s.execute()
        
        return response[:limit]