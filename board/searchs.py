from typing import List
from elasticsearch_dsl import Q
from board.documents import PostDocument


def search_posts(
        query: str = None,
        board_urls: List[str] = None,
        tag_names: List[str] = None,
        sort_fields: List[str] = None,
        page: int = 1,
        page_size: int = 10,
):
    """
    Elasticsearch에서 게시글 검색, Board URL 및 Tag 필터링 포함
    """
    # 기본 정렬 설정
    if sort_fields is None:
        sort_fields = ["-created_at"]

    # 페이지네이션 계산
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    start = (page - 1) * page_size

    # 기본 검색 쿼리 설정
    if query:
        q = Q(
            "bool",
            should=[
                Q("match", title=query),
                Q("match", body=query),
            ],
            minimum_should_match=1
        )
    else:
        q = Q("match_all")  # query가 없을 경우 전체 검색

    # 필터 조건 설정
    filters = [Q("term", is_active=True)]  # 활성화된 게시글만 필터링

    if board_urls:
        filters.append(Q("terms", board__url=board_urls))

    if tag_names:
        filters.append(
            Q(
                "nested",
                path="tag_set",
                query=Q("terms", tag_set__tag_name=tag_names)
            )
        )

    # 필터를 bool 쿼리에 추가
    if filters:
        q = Q("bool", must=[q], filter=filters)

    # Elasticsearch 검색 실행
    search = PostDocument.search().query(q).sort(*sort_fields)[start:start + page_size]
    return search.execute()
