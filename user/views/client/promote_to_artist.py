from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def promote_to_artist(request, slug, pk):
    if request.method != "POST":
        return redirect('/')

    if str(request.user.pk) != str(pk) or request.user.slug != slug:
        messages.error(request, "Ação não autorizada.")
        return redirect('/')

    if not request.user.is_client:
        messages.error(request, "Apenas artistas podem se rebaixar.")
        return redirect('/')

    # Cria o perfil Client e deleta o Artist, os signals cuidam das flags
    request.user.promote_to_artist()

    messages.success(request, "Você voltou a ser um cliente.")
    # Logout ou redireciona para home
    from django.contrib.auth import logout
    logout(request)
    return redirect('/')
