import uuid  # Нужен для уникальных экземпляров книг
from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse  # Используется для генерации URL-адресов


class Genre(models.Model):
    """Модель, представляющая жанр книги (например, научная фантастика, документальная литература)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)",
    )

    def __str__(self):
        """Строка для представления объекта модели (в админ-панели и т.д.)."""
        return self.name


class Language(models.Model):
    """Модель, представляющая язык, на котором написана книга (например, английский, французский)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)",
    )

    def __str__(self):
        return self.name


class Book(models.Model):
    """Модель, представляющая книгу (но не конкретный экземпляр книги)."""
    title = models.CharField(max_length=200)
    # ForeignKey: у книги один автор, но у автора может быть много книг.
    # Author указан строкой, т.к. класс объявлен ниже в файле.
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField(
        'ISBN',
        max_length=13,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )
    # ManyToManyField: книга может относиться к нескольким жанрам, жанр -- к нескольким книгам.
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title']

    def display_genre(self):
        """Строка с жанрами (нужна для отображения жанров в админ-панели)."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """URL для доступа к странице конкретной книги."""
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """Модель, представляющая конкретный экземпляр книги (который можно взять в библиотеке)."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    @property
    def is_overdue(self):
        """Просрочена ли выдача книги."""
        return bool(self.due_back and date.today() > self.due_back)

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title if self.book else 'no book')


class Author(models.Model):
    """Модель, представляющая автора."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """URL для доступа к странице конкретного автора."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return '{0}, {1}'.format(self.last_name, self.first_name)
