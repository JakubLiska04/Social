# api.py
from rest_framework import generics
import random
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Profile, Post
from .serializers import ProfileSerializer, PostSerializer, IndexDataSerializer, UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .decorators import login_required_api


@login_required_api
class IndexAPIView(generics.RetrieveAPIView):
    serializer_class = IndexDataSerializer

    def retrieve(self, request, *args, **kwargs):
        user_object = request.user
        user_profile = Profile.objects.get(user=user_object)
        user_following_list = list(user_profile.following.all())
        user_following_list.append(user_profile)
        feed_list = Post.objects.filter(user__profile__in=user_following_list)
        all_users = User.objects.all()
        user_following_all = user_profile.following.all()
        new_suggestions_list = [x for x in all_users if (
            x not in user_following_all and x != user_object)]
        random.shuffle(new_suggestions_list)

        suggestions_username_profile_list = Profile.objects.filter(
            user__in=new_suggestions_list)[:4]

        data = {
            'user_profile': user_profile,
            'posts': feed_list,
            'suggestions_username_profile_list': suggestions_username_profile_list,
        }
        serializer = IndexDataSerializer(data)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user is not None and user.check_password(password):
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)
