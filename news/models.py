from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
  authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
  ratingAuthor = models.SmallIntegerField(default=0)

  # def __str__(self):
  #   return self.authorUser
  
  def update_rating(self):
    postRat = self.post_set.all().aggregate(postRating=Sum('rating'))
    pRat = 0
    pRat += postRat.get('postRating')

    commentRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('rating'))
    cRat = 0
    cRat += commentRat.get('commentRating')

    self.ratingAuthor = pRat * 3 + cRat
    self.save()


class Category(models.Model):
  name = models.CharField(max_length=64, unique=True)
  subscribers = models.ManyToManyField(User, through='CategorySubscribers')

  class Meta:
    verbose_name = 'Категория'
    verbose_name_plural = 'Категории'
    
  def __str__(self):
    return self.name

class CategorySubscribers(models.Model):
    sub_categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
      return f'{self.sub_categories}, {self.sub_users}'

class Post(models.Model):
  author = models.ForeignKey(Author, on_delete=models.CASCADE)

  NEWS = 'NW'
  ARTICLE = 'AR'
  CATEGORY_CHOICES = (
    (NEWS, 'Новость'),
    (ARTICLE, 'Статья'),
  )
  categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
  dateCreation = models.DateTimeField(auto_now_add=True)
  postCategory = models.ManyToManyField(Category, through='PostCategory')
  title = models.CharField(max_length=128)
  text = models.TextField()
  rating = models.SmallIntegerField(default=0)

  def like(self):
    self.rating += 1
    self.save()

  def dislike(self):
    self.rating -= 1
    self.save()

  def preview(self):
    return self.text[:124] + '...'

  def __str__(self):
    return 'Title: ' + self.title + '; ' + 'Content: ' + self.preview()

  def get_absolute_url(self):
    return f'/news/{self.id}'


class PostCategory(models.Model):
  postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
  categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
  commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
  commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
  text = models.TextField()
  dateCreation = models.DateTimeField(auto_now_add=True)
  rating = models.SmallIntegerField(default=0)

  def __str__(self):
    return self.commentUser.username

  def like(self):
    self.rating += 1
    self.save()

  def dislike(self):
    self.rating -= 1
    self.save()