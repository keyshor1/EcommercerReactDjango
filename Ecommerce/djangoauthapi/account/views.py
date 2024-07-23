from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer, ProductSerializer, ProductDetailSerializer, CategorySerializer, AddCartSerializer, ShowCartSerializer, AddressSerializer, OrderPlacedSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.models import Address, Product, Cart, OrderPlaced

# Create token manually 
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data = request.data)  # Receive the data from request or from frontend and serialize it
        if serializer.is_valid(raise_exception=True):
            user =  serializer.save()
            token = get_tokens_for_user(user) #create token after registration
            return Response({'token': token,'msg': 'Kishor Registration successfull'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user) #create token after login success
                return Response({'token': token, 'msg': 'User Registered'}, status=status.HTTP_200_OK)
            else:
                print(UserRenderer)
                return Response({'errors':{'non_field_errors': ['Username or password is wrong']}}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'email is send successfullly'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'password reset is successfulll'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        productview = Product.objects.all()
        serializer = ProductSerializer(productview, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductDetailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        id=pk
        productdetailview = Product.objects.get(id=id)
        serializer = ProductDetailSerializer(productdetailview)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CategoryView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, val, format=None):
        categoryview = Product.objects.filter(category=val)
        # title = Product.objects.get(category=val).values('title')
        serializer = CategorySerializer(categoryview, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
# class CartView(APIView):
#     def post(self, request, format=None):
#         user = request.user
#         product_id = request.data.get('product_id')
#         product = Product.objects.filter(id=product_id)
#         quantity = request.data.get('quantity', 1)
#         cart_items = {user, product, quantity}
#         serializer = CartSerializer(cart_items, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class AddCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        try:
            # Assuming there's only one product with the given id
            cart_item, created = Cart.objects.get_or_create(user=user, product_id=product_id)
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()
            serializer = AddCartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, *args, **kwargs):
        # Retrieve id from URL parameters
        cart_id = kwargs['pk']
        cart = Cart.objects.get(id=cart_id)
        data = request.data.get('quantity')
        serializer = AddCartSerializer(cart, data={'quantity': data}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShowCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        cart_data = Cart.objects.filter(user=user)
        amount = 0
        for cart in cart_data:
            value = cart.quantity * cart.product.selling_price
            amount = amount +  value
        totalamount = amount + 100
        serializer = ShowCartSerializer(cart_data, many=True)
        context={
            "cart_data": serializer.data,
            "amount": amount,
            "totalamount": totalamount
            }
        return Response(context, status=status.HTTP_200_OK)
    
    
class AddressView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user= request.user
        address_detail = Address.objects.filter(user=user)
        # print(address_detail)
        serializer = AddressSerializer(address_detail, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
            
    def post(self, request, format=None):
        user = request.user
        address_data = {
            'user': user.id,
            'sender_name': request.data.get('sender_name'),
            'receiver_name': request.data.get('receiver_name'),
            'receiver_email': request.data.get('receiver_email'),
            'state': request.data.get('state'),
            'city': request.data.get('city'),
            'locality': request.data.get('locality'),
            'sender_number': request.data.get('sender_number'),
            'receiver_number': request.data.get('receiver_number')
        }
        serializer = AddressSerializer(data=address_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Address Updated'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def post(self, request, format=None):
    #     user = request.user
    #     sender_name =  request.data.get('sender_name')
    #     receiver_name = request.data.get('receiver_name')
    #     receiver_email = request.data.get('receiver_email')
    #     state = request.data.get('state')
    #     city = request.data.get('city')
    #     locality = request.data.get('locality')
    #     sender_number = request.data.get('sender_number')
    #     receiver_number = request.data.get('receiver_number')
    #     address_data = Address.objects.create(user=user, sender_name=sender_name, receiver_name=receiver_name, receiver_email=receiver_email, state=state, city=city, locality=locality, sender_number=sender_number, receiver_number=receiver_number)
    #     serializer = AddressSerializer(data = address_data)
    #     if serializer.is_valid():
    #         return Response({'msg': 'Address Updated'}, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderPlacedView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user= request.user
        address_id = request.data.get('address_id')
        cart = Cart.objects.filter(user=user)
        for c in cart:
            order_placed = OrderPlaced(user=user, address_id=address_id, product=c.product, quantity=c.quantity ).save()
            c.delete()
        serializer = OrderPlacedSerializer(order_placed, many=True)
        if serializer.is_valid():
            print(serializer.data)
            Response( serializer.data, status=status.HTTP_201_CREATED)



