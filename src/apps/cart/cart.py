from decimal import Decimal
from apps.courses.models import Course

CART_SESSION_KEY = 'cart'


class Cart:
    """
    Carrinho baseado em sessão.
    Estrutura: {'<course_id>': {'title': ..., 'price': ..., 'slug': ...}}
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not cart:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, course):
        course_id = str(course.id)
        if course_id not in self.cart:
            self.cart[course_id] = {
                'title': course.title,
                'price': str(course.price),
                'slug': course.slug,
                'cover_image': course.cover_image.url if course.cover_image else '',
            }
            self.save()

    def remove(self, course_id):
        course_id = str(course_id)
        if course_id in self.cart:
            del self.cart[course_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session[CART_SESSION_KEY]
        self.session.modified = True

    def __len__(self):
        return len(self.cart)

    def __iter__(self):
        course_ids = self.cart.keys()
        courses = Course.objects.filter(id__in=course_ids)
        course_map = {str(c.id): c for c in courses}

        for course_id, item in self.cart.items():
            course = course_map.get(course_id)
            if course:
                yield {
                    'course_id': course_id,
                    'course': course,
                    'price': Decimal(item['price']),
                }

    @property
    def total(self):
        return sum(Decimal(item['price']) for item in self.cart.values())

    def contains(self, course_id):
        return str(course_id) in self.cart
