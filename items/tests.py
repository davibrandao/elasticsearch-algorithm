from django.test import TransactionTestCase
from django.core.management import call_command
from elasticsearch_dsl import connections
from .models import Item, Tag
from .services import RecommendationService
from .documents import ItemDocument
from unittest.mock import patch, MagicMock

class RecommendationServiceTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Run migrations
        call_command('migrate')
        # Create the Elasticsearch index
        ItemDocument.init()
        # Rebuild the Elasticsearch index
        call_command('search_index', '--rebuild', '-f')

    def setUp(self):
        # Create test tags
        self.tag1 = Tag.objects.create(name="Programming")
        self.tag2 = Tag.objects.create(name="Web Development")

        # Create test items
        self.item1 = Item.objects.create(
            title="Python Book",
            description="Learn Python programming",
            category="Books",
            popularity_score=0.5
        )
        self.item1.tags.add(self.tag1)
        
        self.item2 = Item.objects.create(
            title="JavaScript Course",
            description="Master JavaScript",
            category="Courses",
            popularity_score=0.7
        )
        self.item2.tags.add(self.tag1, self.tag2)
        
        self.item3 = Item.objects.create(
            title="Python Course",
            description="Advanced Python techniques",
            category="Courses",
            popularity_score=0.6
        )
        self.item3.tags.add(self.tag1)
        
        # Refresh the Elasticsearch index
        ItemDocument._index.refresh()

    def test_get_recommendations(self):
        recommendations = RecommendationService.get_recommendations(self.item1.id, limit=2)
        
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 2)
        self.assertNotEqual(recommendations[0].id, self.item1.id)
        self.assertTrue(any('Python' in item.title for item in recommendations))

    def test_recommendations_exclude_current_item(self):
        recommendations = RecommendationService.get_recommendations(self.item1.id)
        
        self.assertTrue(all(item.id != self.item1.id for item in recommendations))

    def test_recommendations_respect_limit(self):
        recommendations = RecommendationService.get_recommendations(self.item1.id, limit=1)
        
        self.assertEqual(len(recommendations), 1)

    def test_recommendations_for_nonexistent_item(self):
        non_existent_id = max(item.id for item in Item.objects.all()) + 1
        recommendations = RecommendationService.get_recommendations(non_existent_id)
        
        self.assertEqual(len(recommendations), 0)

    @patch('elasticsearch_dsl.Search.execute')
    def test_recommendations_with_elasticsearch_error(self, mock_execute):
        mock_execute.side_effect = Exception("Elasticsearch error")
        
        recommendations = RecommendationService.get_recommendations(self.item1.id)
        
        self.assertEqual(len(recommendations), 0)

    def test_recommendations_with_no_similar_items(self):
        # Create an item with unique attributes
        unique_item = Item.objects.create(
            title="Unique Item",
            description="This item has no similar items",
            category="Unique"
        )
        
        recommendations = RecommendationService.get_recommendations(unique_item.id)
        
        self.assertEqual(len(recommendations), 0)

    @patch('items.services.RecommendationService.build_search')
    def test_recommendations_query_structure(self, mock_build_search):
        mock_search = MagicMock()
        mock_build_search.return_value = mock_search
        mock_search.execute.return_value = MagicMock()

        RecommendationService.get_recommendations(self.item1.id)

        # Check if build_search was called
        mock_build_search.assert_called_once()
        
        # Check the query structure
        args, kwargs = mock_build_search.call_args
        query = args[0]
        self.assertIn('function_score', query)
        self.assertIn('query', query['function_score'])
        self.assertIn('multi_match', query['function_score']['query'])

    def tearDown(self):
        # Clear the Elasticsearch index
        ItemDocument._index.delete(ignore=404)