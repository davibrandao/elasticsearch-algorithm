from django.shortcuts import render, get_object_or_404
from elasticsearch_dsl import Q
from .documents import ItemDocument
from django.core.paginator import Paginator
from elasticsearch_dsl.aggs import A
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import RecommendationService
from .serializers import ItemSerializer
from .models import Item
import logging

logger = logging.getLogger(__name__)

def search_items(request):
    q = request.GET.get('q')
    category = request.GET.get('category')
    page = request.GET.get('page', 1)

    # Start with a match all query
    search = ItemDocument.search()

    if q:
        query = Q('multi_match', query=q, fields=['title', 'description'])
        search = search.query(query)
    
    if category:
        search = search.filter('term', category=category)
    
    # Add aggregation for categories
    search.aggs.bucket('categories', 'terms', field='category')
    
    search = search.extra(size=1000)  # Increase size to get all results for pagination
    response = search.execute()
    
    # Get facets
    category_facets = response.aggregations.categories.buckets
    
    # Get all items from the search results
    all_items = [Item.objects.get(id=hit.meta.id) for hit in response]

    # Get recommendations for each item
    results = []
    for item in all_items:
        recommendations = RecommendationService.get_recommendations(item.id, limit=3)
        results.append({
            'item': item,
            'recommendations': recommendations
        })

    # Paginate results
    paginator = Paginator(results, 10)  # 10 items per page
    page_results = paginator.get_page(page)

    context = {
        'results': page_results,
        'query': q,
        'category_facets': category_facets,
        'selected_category': category,
    }
    return render(request, 'items/search.html', context)

class RecommendationView(APIView):
    def get(self, request, item_id):
        limit = request.query_params.get('limit', 5)
        recommendations = RecommendationService.get_recommendations(item_id, limit=int(limit))
        serializer = ItemSerializer(recommendations, many=True)
        return Response(serializer.data)

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    recommendations = RecommendationService.get_recommendations(item.id, limit=3)
    return render(request, 'items/item_detail.html', {'item': item, 'recommendations': recommendations})

