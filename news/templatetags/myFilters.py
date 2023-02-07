from django import template

register = template.Library()

@register.filter(name='Censor')
def Censor(value, arg = 'Вонючка'):
  if isinstance(value, str) and isinstance(arg, str):
    value_arr = value.split(' ')
    new_value = []
    for word in value_arr:
      if arg.lower() not in word.lower():
        new_value.append(word)
      else:
        new_value.append('*ЦЕНЗУРА*')
    return ' '.join(new_value)
  
  else: raise ValueError('Введите слово, которое нужно заменить')