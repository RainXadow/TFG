from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.files.base import ContentFile
from django.utils.http import urlsafe_base64_decode
from django.core import serializers
from django.http import JsonResponse
from .froms import PostCreateForm, PostUpdateForm
from .models import Post, Comment, Evaluation
from django.db.models import Q
from django.views.generic import ListView

class BlogListView(LoginRequiredMixin, View): 
    login_url = 'usuario:login'

    def get(self, request, *args, **kwargs):
        start = int(request.GET.get('start', 0))
        end = start + 6
        filter = request.GET.get('filter', 'all')
        query = request.GET.get('q')

        order_param = request.GET.get('order', 'newest')  # Defecto a 'newest'
        order_mapping = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'most_stars': '-evaluation',
            'most_users': '-user_participation'            
        }
        order = order_mapping.get(order_param, '-created_at')  # Fallback a '-created_at' si el order_param no es válido

        if query:  # Si es una búsqueda
            if filter == 'my_posts':
                posts = Post.objects.filter(author=request.user, title__icontains=query).order_by(order)[start:end]
            else:
                posts = Post.objects.filter(title__icontains=query).order_by(order)[start:end]
        else:  # Si es filtrado y ordenamiento
            if filter == 'my_posts':
                posts = Post.objects.filter(author=request.user).order_by(order)[start:end]
            else:
                posts = Post.objects.all().order_by(order)[start:end]

        data = []   
        for post in posts:
            data.append({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "image": post.image.url if post.image else None,
                "evaluation": post.evaluation,
                "user_participation": post.user_participation,
                "is_author": post.author == request.user,
                "detail_url": request.build_absolute_uri(reverse('blog:detail', args=[post.id])),
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(data, safe=False)

        return render(request, 'blog_list.html', {'posts': data[:6]})

        
class BlogCreateView(LoginRequiredMixin, View):
    login_url = 'usuario:login'  # Actualiza este valor según el nombre de la URL de inicio de sesión en tu proyecto

    def get(self, request, *args, **kwargs):
        form = PostCreateForm()
        form.fields['title'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['content'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded resize-none', 'rows': '5'})
        form.fields['evaluation'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['image'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['price'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['where_to_find'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})

        context = {
            'form': form
        }
        return render(request, 'blog_create.html', context)
    
    def post(self, request, *args, **kwargs):
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('blog:home')
        else:
            print("Formulario no válido:", form.errors)
            
        context = {
            'form': form
        }
        return render(request, 'blog_create.html', context)

class BlogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = 'usuario:login'  # Actualiza este valor según el nombre de la URL de inicio de sesión en tu proyecto

    model = Post
    form_class = PostUpdateForm
    template_name = 'blog_update.html'
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        form.fields['title'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['content'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded resize-none', 'rows': '5'})
        form.fields['evaluation'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['price'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})
        form.fields['where_to_find'].widget.attrs.update({'class': 'bg-gray-700 text-white w-full px-3 py-2 rounded'})

        context = {
        'form': form,
        'object': self.object,
        'form_errors': form.errors,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        print("Método post llamado")
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('blog:home')
    
    def form_valid(self, form):
        post = form.save(commit=False)
        delete_image = self.request.POST.get('delete_image', '')
        if delete_image == 'true':
            post.image.delete()
        
        post.save()
        messages.success(self.request, 'Post actualizado con éxito.')
        return HttpResponseRedirect(self.get_success_url())
    
class BlogDetailView(LoginRequiredMixin, View):
    login_url = 'usuario:login'

    def get(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        evaluations = Evaluation.objects.filter(post=post)
        context = {
            'post': post,
            'comments': comments,
            'evaluations': evaluations,
        }
        return render(request, 'blog_detail.html', context)
    
class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        comment_text = request.POST.get('comment_text')
        Comment.objects.create(post=post, author=request.user, comment_text=comment_text)
        return redirect('blog:detail', pk=post.pk)

class AddEvaluationView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        rating = request.POST.get('rating')
        # Intenta obtener la evaluación existente
        evaluation, created = Evaluation.objects.get_or_create(
            post=post, 
            author=request.user, 
            defaults={'rating': rating},
        )
        # Si la evaluación es nueva, incrementa la participación del usuario
        if created:
            post.user_participation += 1
            post.save()
        # Si la evaluación ya existía, actualiza su calificación
        if not created:
            evaluation.rating = rating
            evaluation.save()
        # Recalcula la evaluación del post
        ratings = [evaluation.rating for evaluation in post.evaluations.all()]
        total_evaluations = len(ratings)
        total_score = sum(ratings)
        # Solo cuenta la evaluación inicial si no hay evaluaciones de usuarios
        if total_evaluations == 0:
            total_evaluations += 1
            total_score += post.evaluation
        post.evaluation = total_score / total_evaluations
        post.save()
        return redirect('blog:detail', pk=post.pk)

    
class BlogDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'usuario:login'  # Actualiza este valor según el nombre de la URL de inicio de sesión en tu proyecto

    model = Post
    template_name = 'blog_delete.html'
    success_url = reverse_lazy('blog:home')