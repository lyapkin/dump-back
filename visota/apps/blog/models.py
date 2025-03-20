from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from ckeditor.fields import RichTextField
from parler.models import TranslatableModel, TranslatedFields
from common.utils import generate_unique_slug, generate_unique_slug_translated

from common.utils import CustomStorage


class PostRedirectFrom(models.Model):
  to = models.ForeignKey('Post', on_delete=models.CASCADE)
  old_slug = models.CharField("старый url", max_length=60, unique=True)
  lang = models.CharField('языковая версия поста старого url', max_length=2, choices=settings.LANGUAGES, default='ru')

  # class Meta:
  #   constraints = [
  #     models.UniqueConstraint(fields=['old_slug', 'lang'], name='unique_slug_for_lang'),
  #   ]

  def __str__(self):
    post = self.to
    post.set_current_language('ru')
    return f'язык: {self.lang}; старый слаг: {self.old_slug}; к: {post.title}'
    
  class Meta:
    verbose_name = "Старый слаг (редирект (seo))"
    verbose_name_plural = "Старые слаги (редиректы (seo))"


def validate_is_slug_old(value):
  result = PostRedirectFrom.objects.filter(old_slug=value).exists()
  if result:
      raise ValidationError('Этот slug уже использовался')


class Post(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField("заголовок", max_length=100, unique=True),
        slug = models.SlugField("url", max_length=250, unique=True, blank=True, validators=[validate_is_slug_old]),
        content = CKEditor5Field("текст статьи", config_name='extends2'),
        # content = RichTextField("текст статьи"),
        content_concise = models.TextField("краткое описание статьи", max_length=120),
        date = models.DateField("дата", auto_now_add=True),
        last_modified = models.DateField(auto_now=True)
    )
    image_url = models.ImageField("изображение", storage=CustomStorage)

    def save(self, *args, **kwargs):
        if not self.slug.strip():
            self.slug = generate_unique_slug_translated(Post, Post.postredirectfrom_set.rel.related_model, self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "пост"
        verbose_name_plural = "посты"