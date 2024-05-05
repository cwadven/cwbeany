from django.core.paginator import Paginator


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
