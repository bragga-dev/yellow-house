
from django.shortcuts import render
from vitrine.models import Blog
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator



def blog_list(request):
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')

    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)

    context = {
        'blogs': blogs
    }
    return render(request, 'vitrine/blog_list.html', context)


def blog_detail(request, slug, blog_id):
    blog = get_object_or_404(Blog, slug=slug, id=blog_id, is_published=True)

    context = {
        'blog': blog
    }
    return render(request, 'vitrine/blog_detail.html', context)



