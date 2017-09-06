from django.http import HttpResponse

def home(request):
    output = "<h1>Career Aware Application</h1><br/><a href='/admin'>Click here to login</a>"
    return HttpResponse(output)
