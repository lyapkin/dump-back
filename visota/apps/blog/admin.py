from django import forms
from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Post, PostRedirectFrom

# Register your models here.

class PostAdminForm(forms.ModelForm):
    title = forms.CharField()
    content_concise = forms.CharField(widget=forms.Textarea)
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        exclude = ('translations__slug',)


class PostRedirectFromInline(admin.TabularInline):
  model = PostRedirectFrom
  extra = 1


class PostAdmin(TranslatableAdmin):
  # form = PostAdminForm
  # prepopulated_fields = {"slug": ("title",)}
  list_display = ["title", "date"]

  def get_queryset(self, request):
      # Limit to a single language!
      language_code = self.get_queryset_language(request)
      return super(PostAdmin, self).get_queryset(request).translated(language_code)
  
  inlines = (PostRedirectFromInline,)

admin.site.register(Post, PostAdmin)