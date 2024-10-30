from django.contrib import admin
from .models import Question, Subquestion, Phrase, User, QueryHistory



class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'created_at')
    search_fields = ('username', 'telegram_id')
    ordering = ('created_at',)


class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'created_at')
    search_fields = ('user__username', 'question')
    ordering = ('-created_at',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_confidence')
    search_fields = ('name',)


class SubquestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'question', 'min_confidence')
    search_fields = ('name',)


class PhraseAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'subquestion')
    search_fields = ('text',)


# Регистрация моделей
admin.site.register(User, UserAdmin)
admin.site.register(QueryHistory, QueryHistoryAdmin)

# Регистрация остальных моделей в отдельном разделе
admin.site.register(Question, QuestionAdmin)
admin.site.register(Subquestion, SubquestionAdmin)
admin.site.register(Phrase, PhraseAdmin) 
 
# Настройка заголовка админки
admin.site.site_header = "Админка поддержки бота"  
admin.site.site_title = "Панель управления"
admin.site.index_title = "Управление ботом"
