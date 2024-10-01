REPLY_NOTIFICATION = 'reply_notification'
REREPLY_NOTIFICATION = 'rereply_notification'
LIKE_NOTIFICATION = 'like_notification'
HEALTH_CHECK = 'health_check'
POST_SUMMARY_ISSUE = 'post_summary_issue'
BACKUP_SQL = 'backup_sql'
BACKUP_MEDIA = 'backup_media'


EMAIL_TEMPLATE_MAPPER = {
    REPLY_NOTIFICATION: 'email/notification/reply_notification.html',
    REREPLY_NOTIFICATION: 'email/notification/rereply_notification.html',
    LIKE_NOTIFICATION: 'email/notification/like_notification.html',
    HEALTH_CHECK: 'email/common/health_check.html',
    BACKUP_SQL: 'email/common/backup_sql.html',
    POST_SUMMARY_ISSUE: 'email/common/post_summary_issue.html',
    BACKUP_MEDIA: 'email/common/backup_media.html',
}
