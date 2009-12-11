from django.contrib import admin
from disqus.models import Forum, Thread, Post, AnonymousAuthor, Author

class ForumAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        context = {
            'has_add_permission': False,
        }
        return super(ForumAdmin, self).changelist_view(request,
            extra_context=context)

admin.site.register(Forum, ForumAdmin)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(AnonymousAuthor)
admin.site.register(Author)
