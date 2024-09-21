from django.http import JsonResponse
from chatgpt.services import get_latest_post_summary_by_post_id


def get_summary_by_post_id(request, post_id: int):
    if post_id is None:
        return JsonResponse({'error': 'post_id is required'}, status=400)

    post_summary = get_latest_post_summary_by_post_id(post_id)
    context = {
        'status': post_summary.status if post_summary else None,
        'summary': post_summary.body if post_summary else None,
    }
    return JsonResponse(context, status=200)
