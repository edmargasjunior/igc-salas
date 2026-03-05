"""Context processor para notificações não lidas."""


def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        from .models import Notificacao
        count = Notificacao.objects.filter(
            destinatario=request.user,
            lida=False
        ).count()
        return {'notificacoes_nao_lidas': count}
    return {'notificacoes_nao_lidas': 0}
