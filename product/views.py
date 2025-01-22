import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()




def fetch_product_data(artikul):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        products = json_data.get('data', {}).get('products', [])
        if not products:  # `products` bo'sh bo'lsa
            return None

        data = products[0]  # Birinchi mahsulotni olish
        product, _ = Product.objects.update_or_create(
            artikul=artikul,
            defaults={
                'name': data['name'],
                'price': data['priceU'] / 100,
                'rating': data.get('rating', 0),
                'total_quantity': sum(stock['qty'] for stock in data['sizes'][0]['stocks']),
            }
        )
        return product
    return None


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class AllProductsView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductView(APIView):

    def post(self, request, *args, **kwargs):
        artikul = request.data.get('artikul')
        if not artikul:
            return Response({"error": "Artikul is required"}, status=400)
        product = fetch_product_data(artikul)
        if product:
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        return Response({"error": "Product not found"}, status=404)

class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, artikul, *args, **kwargs):
        def periodic_task():
            fetch_product_data(artikul)

        scheduler.add_job(
            periodic_task,
            'interval',
            minutes=30,
            id=f"update_{artikul}",
            replace_existing=True
        )
        return Response({"message": f"Subscription started for artikul {artikul}"})
