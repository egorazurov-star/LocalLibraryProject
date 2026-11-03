import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre, Language


def index(request):
    """Функция отображения для домашней страницы сайта."""
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # Метод 'all()' применён по умолчанию.
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()

    # Количество посещений этого представления, подсчитанное в переменной сессии
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={
            'num_books': num_books,
            'num_instances': num_instances,
            'num_instances_available': num_instances_available,
            'num_authors': num_authors,
            'num_genres': num_genres,
            'num_visits': num_visits,
        },
    )


class BookListView(generic.ListView):
    """Список всех книг (с постраничным выводом)."""
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    """Подробная информация о книге."""
    model = Book


class AuthorListView(generic.ListView):
    """Список всех авторов."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Подробная информация об авторе."""
    model = Author


class GenreListView(generic.ListView):
    """Список всех жанров."""
    model = Genre
    paginate_by = 10


class LanguageListView(generic.ListView):
    """Список всех языков."""
    model = Language
    paginate_by = 10


class BookInstanceListView(generic.ListView):
    """Список всех экземпляров (копий) книг."""
    model = BookInstance
    paginate_by = 10


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Книги, взятые текущим пользователем."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Все взятые книги -- видно только библиотекарям (право can_mark_returned)."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """Продление конкретного экземпляра книги библиотекарем."""
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # Если это POST-запрос, обрабатываем данные формы
    if request.method == 'POST':
        # Создаём экземпляр формы и заполняем его данными из запроса (связывание)
        form = RenewBookForm(request.POST)

        if form.is_valid():
            # Записываем новую дату в поле due_back модели
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # Перенаправляем на страницу со всеми выданными книгами
            return HttpResponseRedirect(reverse('all-borrowed'))

    # Если это GET (или другой метод), создаём форму по умолчанию
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})


# ---- Формы для Author (CreateView / UpdateView / DeleteView) ----

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '2016-12-10'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


# ---- Формы для Book ("Проверьте себя" из части 9) ----

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'


# ---- Формы для Genre, Language и BookInstance ----

class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name']
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.can_mark_returned'


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name']
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.can_mark_returned'


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = '__all__'
    success_url = reverse_lazy('bookinstances')
    permission_required = 'catalog.can_mark_returned'
