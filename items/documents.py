from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Item

@registry.register_document
class ItemDocument(Document):
    title = fields.TextField()
    description = fields.TextField()
    created_at = fields.DateField()
    category = fields.KeywordField()
    tags = fields.KeywordField(multi=True)
    popularity_score = fields.FloatField()

    class Index:
        name = 'items'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Item
        fields = [
            'id',
        ]

    def prepare_tags(self, instance):
        return [tag.name for tag in instance.tags.all()]