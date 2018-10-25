from django import template

register = template.Library()

@register.filter(name="index")
def index(List, i):
    return List[int(i)]


@register.simple_tag
def GetHash():
    try:
        with open("githash", "r") as stream:
            h = stream.readlines()[0].strip('\n')
        return h
    except:
        return "None"