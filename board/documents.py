from django_elasticsearch_dsl import (
    Document,
    fields,
)
from django_elasticsearch_dsl.registries import registry
from board.models import Post


@registry.register_document
class PostDocument(Document):
    title = fields.TextField(analyzer="korean_analyzer")
    body = fields.TextField(analyzer="korean_analyzer")
    post_img = fields.KeywordField()
    board = fields.ObjectField(
        properties={
            "url": fields.KeywordField(),
        }
    )
    author = fields.ObjectField(
        enabled=False,  # 색인하지 않음, 조회에서만 사용
        properties={
            "id": fields.IntegerField(),
            "username": fields.KeywordField(),
            "nickname": fields.KeywordField(),
        }
    )
    tag_set = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "tag_name": fields.TextField(analyzer="korean_analyzer"),
        }
    )

    class Index:
        # Define the Elasticsearch index name
        name = 'posts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            "analysis": {
                "analyzer": {
                    "korean_analyzer": {
                        "type": "custom",
                        "tokenizer": "nori_tokenizer",
                        "filter": ["lowercase"]
                    }
                }
            }
        }

    class Django:
        model = Post  # Django 모델과 연결
        fields = [
            'like_count',
            'reply_count',
            'rereply_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
