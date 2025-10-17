
from django.shortcuts import render
from vitrine.models import Blog
from django.shortcuts import get_object_or_404






def blog_list(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')

    context = {
        'blogs': blogs
    }
    return render(request, 'vitrine/blog_list.html', context)


def blog_view(request, slug, blog_id):
    blog = get_object_or_404(Blog, slug=slug, id=blog_id)

    context = {
        'blog': blog
    }
    return render(request, 'vitrine/blog.html', context)



