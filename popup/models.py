from django.db import models


class Popup(models.Model):
    image = models.TextField(verbose_name='이미지', blank=True, null=True)
    description = models.TextField(verbose_name='관리자 보기 위한 설명', blank=True, null=True)
    on_click_link = models.TextField(verbose_name='이미지 클릭 시 링크', null=True)
    height = models.PositiveIntegerField(verbose_name='모달 높이')
    width = models.PositiveIntegerField(verbose_name='모달 너비')
    sequence = models.PositiveIntegerField(
        verbose_name='앞에 있는 순서',
        default=1,
        help_text='숫자가 작을수록 앞에 있음',
        db_index=True,
    )
    start_time = models.DateTimeField(verbose_name='시작 시간', blank=True, null=True, db_index=True)
    end_time = models.DateTimeField(verbose_name='종료 시간', blank=True, null=True, db_index=True)
    is_active = models.BooleanField(verbose_name='활성화 여부', default=False)
    created_at = models.DateTimeField(verbose_name='생성 시간', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정 시간', auto_now=True)

    class Meta:
        abstract = True


class HomePopupModal(Popup):
    objects = models.Manager()

    class Meta:
        verbose_name = '홈 팝업 모달'
        verbose_name_plural = '홈 팝업 모달'

    def __str__(self):
        return f'{self.id} - {self.description}'
