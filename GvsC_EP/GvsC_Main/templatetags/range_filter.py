from django.template import Library

register = Library()

@register.filter
def get_range( value ):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return range( value )

@register.filter    
def loop_to_multipule(value, arg):
    additional_loops = 0
    
    remainder = value % arg
    if remainder == 0:
        return additional_loops
        
    next_closest_multipule = value + arg - remainder
    difference = next_closest_multipule - value
    
    return range(difference)