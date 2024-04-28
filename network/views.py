from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils.timezone import now, timedelta
from datetime import datetime
from django.http import JsonResponse
from django.db import transaction
from .forms import OrderForm, JobListingForm, ApplicationForm, EventForm, SignupForm, SigninForm
from .models import Profile, Post, Payment, AccountStatistics, FriendRequest, JobListing, Event, PostRating
import random
import calendar

@login_required(login_url='signin')
def index(request):
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

    context = {
        'user_profile': user_profile,
        'posts': feed_list,
        'suggestions_username_profile_list': suggestions_username_profile_list,
        'base.html': "base.html"
    }
    return render(request, 'index.html', context)


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')

    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_objects = User.objects.filter(username__icontains=username)

        username_profile_list = []

        for user in username_objects:
            profile = Profile.objects.get(user=user)
            username_profile_list.append(profile)

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


def update_rating(request):
    if request.method == 'POST':
        post_id = request.GET.get('post_id')
        rating = int(request.POST.get('rating', 0))

        try:
            post = Post.objects.get(id=post_id)

            post_rating, created = PostRating.objects.get_or_create(
                post=post, user=request.user, defaults={'rating': rating}
            )
            total_points = PostRating.objects.filter(
                post=post).aggregate(Sum('rating'))['rating__sum']
            post.rating = total_points
            post.save()

            return JsonResponse({'success': True, 'new_rating': total_points, 'total_points': total_points})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid rating'})
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Post not found'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required(login_url='signin')
def profile(request, username):
    user_object = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    user_post_length = len(user_posts)

    follower_profile = Profile.objects.get(user=request.user)

    if follower_profile.following.filter(id=user_profile.id).exists():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def freelancer(request, username):
    user_object = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    user_post_length = len(user_posts)

    follower_profile = Profile.objects.get(user=request.user)

    if follower_profile.following.filter(id=user_profile.id).exists():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
    }
    return render(request, 'freelancer.html', context)


@login_required
@transaction.atomic
def toggle_follow(request, user_id):
    if request.method == 'GET' and request.user.is_authenticated:
        user = User.objects.get(pk=user_id)
        if user != request.user:
            try:
                profile = Profile.objects.get(user=user)
                user_profile = Profile.objects.get(user=request.user)
                if profile in user_profile.following.all():
                    user_profile.following.remove(profile)
                    is_following = False
                    profile.follower_count -= 1
                else:
                    user_profile.following.add(profile)
                    is_following = True
                    profile.follower_count += 1

                profile.save()

                return JsonResponse({'status': 'success', 'is_following': is_following, 'follower_count': profile.follower_count})
            except Profile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Profile not found'})
    return JsonResponse({'status': 'error', 'message': 'Authentication required'})


def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()
                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('profile', username=user.username)
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Use email as username
        user = auth.authenticate(request, username=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


def events(request, year=None, month=None):
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    year = int(year)
    month = int(month)
    month_calendar = calendar.monthcalendar(year, month)

    events = Event.objects.filter(
        start_date__year=year, start_date__month=month)

    month_name = calendar.month_name[month]

    current_year = datetime.now().year
    current_month = datetime.now().month

    context = {
        'year': year,
        'month': month,
        'month_calendar': month_calendar,
        'events': events,
        'year_default': year,
        'month_default': month,
        'current_year': current_year,
        'current_month': current_month,
        'month_name': month_name,
    }
    return render(request, 'events.html', context)


def events_date(request, year=None, month=None, day=None):
    current_year = datetime.now().year
    current_month = datetime.now().month

    year = int(year)
    month = int(month)
    month_calendar = calendar.monthcalendar(year, month)

    events = Event.objects.filter(
        start_date__year=year, start_date__month=month)

    context = {
        'current_year': current_year,
        'current_month': current_month,
        'day': day,
        'month_calendar': month_calendar,
        'events': events,
    }
    return render(request, 'events_date.html', context)


def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_calendar')
    else:
        form = EventForm()

    context = {
        'form': form,
    }
    return render(request, 'create_event.html', context)


@login_required(login_url='signin')
def send_friend_request(request, user_id):
    recipient_profile = get_object_or_404(Profile, user_id=user_id)
    sender_profile = request.user.profile
    existing_request = FriendRequest.objects.filter(
        from_user=sender_profile, to_user=recipient_profile, status='pending').first()

    if existing_request:
        messages.error(
            request, 'You have already sent a friend request to this user.')
        return redirect('profile', username=recipient_profile.user.username)
    reverse_request = FriendRequest.objects.filter(
        from_user=recipient_profile, to_user=sender_profile, status='pending').first()

    if reverse_request:
        reverse_request.status = 'accepted'
        reverse_request.save()
        friend_request = FriendRequest.objects.create(
            from_user=sender_profile, to_user=recipient_profile, status='accepted')
        friend_request.save()

        messages.success(
            request, f'You and {recipient_profile.user.username} are now friends!')
    else:
        friend_request = FriendRequest.objects.create(
            from_user=sender_profile, to_user=recipient_profile, status='pending')
        friend_request.save()

        messages.success(
            request, f'Friend request sent to {recipient_profile.user.username}.')

    return redirect('profile', username=recipient_profile.user.username)


@login_required(login_url='signin')
def friends_list(request):
    friends = User.objects.filter(
        friend_requests_received__status='accepted', friend_requests_received__from_user=request.user)
    pending_friend_requests = FriendRequest.objects.filter(
        to_user=request.user, status='pending')

    user_profile = Profile.objects.get(user=request.user)
    user_following_all = user_profile.following.all()
    all_users = User.objects.exclude(
        Q(id=request.user.id) | Q(id__in=user_following_all))
    suggestions_username_profile_list = Profile.objects.filter(
        user__in=all_users)[:4]

    return render(request, 'friends.html', {
        'friends': friends,
        'pending_friend_requests': pending_friend_requests,
        'suggestions_username_profile_list': suggestions_username_profile_list,
    })


@login_required(login_url='signin')
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if request.user == friend_request.to_user and friend_request.status == 'pending':
        friend_request.status = 'accepted'
        friend_request.save()

    return redirect('friends_list')


@login_required(login_url='signin')
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, pk=request_id)

    if friend_request.to_user == request.user:

        friend_request.status = 'rejected'
        friend_request.save()

    return redirect('friends_list')


@login_required(login_url='signin')
def jobs(request):
    return render(request, 'jobs.html')


@login_required(login_url='signin')
def order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order')
    else:
        form = OrderForm()

    context = {
        'form': form,
    }
    return render(request, 'order.html', context)


@login_required(login_url='signin')
def payments(request):
    return render(request, 'payments.html')


def payment_list(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/payment_list.html', {'payments': payments})


@login_required(login_url='signin')
def sell(request):
    return render(request, 'sell.html')


@login_required(login_url='signin')
def statistics(request, period='daily'):
    user = request.user
    today = now()
    if period == 'daily':
        start_date = today - timedelta(days=1)
    elif period == 'weekly':
        start_date = today - timedelta(weeks=1)
    else:
        start_date = None

    if start_date is not None:
        stats = AccountStatistics.objects.filter(
            user=user,
            start_date__gte=start_date,
            end_date__lte=today
        ).aggregate(
            money_spent=Sum('money_spent'),
            jobs_hired=Sum('jobs_hired'),
            earnings=Sum('earnings'),
            followers=Sum('followers'),
        )

    else:
        stats = None

    return render(request, 'statistics.html', {'statistics': stats})


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None


@login_required(login_url='signin')
def job_listing_list(request):
    job_listings = JobListing.objects.all()
    return render(request, 'jobs.html', {'job_listings': job_listings})


@login_required(login_url='signin')
def create_job_listing(request):
    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            job_listing = form.save(commit=False)
            job_listing.save()
            return redirect('job_listing_detail', job_listing.id)
    else:
        form = JobListingForm()
    return render(request, 'create_job_listing.html', {'form': form})


@login_required(login_url='signin')
def job_listing_detail(request, job_listing_id):
    job_listing = get_object_or_404(JobListing, id=job_listing_id)
    return render(request, 'job_listing_detail.html', {'job_listing': job_listing})


@login_required(login_url='signin')
def apply_for_job(request, job_listing_id):
    job_listing = get_object_or_404(JobListing, id=job_listing_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job_listing = job_listing
            application.save()
            return redirect('job_listing_detail', job_listing_id)
    else:
        form = ApplicationForm()
    return render(request, 'apply_for_job.html', {'form': form})
