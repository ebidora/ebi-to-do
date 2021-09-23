from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

# for login
class CustomLoginView(LoginView):
    template_name = 'ebi_todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    # redirect user to tasks if user success to login corectly
    def get_success_url(self):
        return reverse_lazy('tasks')

# for register
class RegisterPage(FormView):
    template_name = 'ebi_todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    # let user log in if user's info is correct
    def form_valid(self,form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage,self).form_valid(form)
    # Make the register page invisible to logged in users
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage,self).get(*args, **kwargs)


# for getting all tasks
class TaskList(LoginRequiredMixin,ListView):
    model = Task
    context_object_name = 'tasks'
    # To allow users to see only their own articles
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Limit to user's own articles
        context['tasks'] = context['tasks'].filter(user = self.request.user)
        context['count'] = context['tasks'].filter(complete= False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
            title__icontains = search_input)
        context['search_input'] = search_input
        return context

# for getting task detail
class TaskDetail(LoginRequiredMixin,DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'ebi_todo/task.html'

# for create new task
class TaskCreate(LoginRequiredMixin,CreateView):
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')
    # To allow users to post only their own articles.
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate,self).form_valid(form)

#for updating task
class TaskUpdate(LoginRequiredMixin,UpdateView):
    model = Task
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')

#for deleting list
class TaskDelete(LoginRequiredMixin,DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
