"""Middlewares customizados do IGC Salas."""
import logging
import time

logger = logging.getLogger('apps')


class AuditLogMiddleware:
    """Registra todas as ações POST/PUT/DELETE para auditoria."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log apenas ações de escrita
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anônimo'
            logger.info(
                f"AUDIT | {request.method} {request.path} | "
                f"User: {username} | IP: {self._get_ip(request)} | "
                f"Status: {response.status_code}"
            )
        return response

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class RequestLoggingMiddleware:
    """Log de performance de requisições lentas."""

    SLOW_REQUEST_THRESHOLD = 2.0  # segundos

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} "
                f"levou {duration:.2f}s"
            )
        return response
