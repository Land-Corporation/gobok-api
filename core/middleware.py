from django.http import HttpResponse


class ELBHealthCheckMiddleware:
    """ ELB health check handler, trouble shooting http/1.1" 400 26
    "-" "ELB-HealthChecker/2.0  in EC2 Instance
    Refer: https://stackoverflow.com/questions/27720254/django-allowed-hosts-with-elb-healthcheck
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health':
            return HttpResponse('ok')
        return self.get_response(request)
