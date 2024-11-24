from django.core.paginator import Paginator
from elasticsearch_dsl import Search


def web_paging(object_list, current_page=1, post_size=10, page_num_size=5):
    """
    request: http request
    object_list: Iterable of objects
    current_page: Current Page Number
    page_num_size: 페이지네이션 번호 보여질 개수 (1,2,3,4: 4개 / 1,2,3: 3개)
    return: page_posts(paginator_queryset) / page_range(number_range)
    """
    posts = Paginator(object_list, post_size)

    max_index = len(posts.page_range)
    start_index = int((current_page - 1) / page_num_size) * page_num_size
    end_index = start_index + page_num_size

    if end_index >= max_index:
        end_index = max_index

    page_range = posts.page_range[start_index:end_index]
    page_posts = posts.get_page(current_page)

    return {
        "page_posts": page_posts,
        "page_range": page_range,
    }


def elasticsearch_paging(
    search_query: Search,
    current_page: int = 1,
    post_size: int = 10,
    page_num_size: int = 5,
):
    """
    Elasticsearch 결과에 페이지네이션을 적용
    :param search_query: Elasticsearch DSL Search 객체
    :param current_page: 현재 페이지 번호
    :param post_size: 페이지당 문서 개수
    :param page_num_size: 페이지네이션 번호 개수
    :return: {
        "page_posts": Elasticsearch 결과 (현재 페이지 데이터),
        "page_range": 페이지네이션 번호 범위,
        "has_previous": 이전 페이지 여부,
        "has_next": 다음 페이지 여부,
        "total_pages": 총 페이지 수,
        "total_count": 총 문서 수,
    }
    """
    # 총 문서 수 계산
    total_count = search_query.count()

    # 총 페이지 수 계산
    total_pages = (total_count + post_size - 1) // post_size

    # 페이지 범위 계산
    max_index = total_pages
    start_index = int((current_page - 1) / page_num_size) * page_num_size
    end_index = start_index + page_num_size

    if end_index > max_index:
        end_index = max_index

    page_range = range(start_index + 1, end_index + 1)

    # 현재 페이지 데이터 가져오기
    start = (current_page - 1) * post_size
    search_query = search_query[start:start + post_size]
    page_posts = search_query.execute()

    # 이전/다음 페이지 여부 계산
    has_previous = current_page > 1
    has_next = current_page < total_pages

    return {
        "page_posts": page_posts,
        "page_range": page_range,
        "has_previous": has_previous,
        "has_next": has_next,
        "total_pages": total_pages,
        "total_count": total_count,
    }
