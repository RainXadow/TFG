from django.urls import path
from .views import BlogListView, BlogCreateView, BlogDetailView, BlogUpdateView, BlogDeleteView, AddCommentView, AddEvaluationView

app_name="blog"

urlpatterns = [
    path('', BlogListView.as_view(), name="home"),
    path('create/', BlogCreateView.as_view(), name="create"),
    path('<int:pk>/', BlogDetailView.as_view(), name='detail'),
    path('<int:pk>/add_comment', AddCommentView.as_view(), name='add_comment'),
    path('<int:pk>/add_evaluation', AddEvaluationView.as_view(), name='add_evaluation'),
    path('<int:pk>/update/', BlogUpdateView.as_view(), name="update"),
    path('<int:pk>/delete/', BlogDeleteView.as_view(), name="delete"),
]
