REPLY_NOTIFICATION = 'reply_notification'
REREPLY_NOTIFICATION = 'rereply_notification'
LIKE_NOTIFICATION = 'like_notification'
HEALTH_CHECK = 'health_check'


EMAIL_TEMPLATE_MAPPER = {
    REPLY_NOTIFICATION: 'email/notification/reply_notification.html',
    REREPLY_NOTIFICATION: 'email/notification/rereply_notification.html',
    LIKE_NOTIFICATION: 'email/notification/like_notification.html',
    HEALTH_CHECK: 'email/common/health_check.html',
}
