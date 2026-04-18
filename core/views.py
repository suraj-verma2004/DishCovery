import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Restaurant, Profile, Activity
from django.contrib import messages
from django.db.models import Q, Count  
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from .models import Restaurant, Profile, Activity, Report  


# AUTH SECTION
def index(request):
    if request.user.is_authenticated: return redirect('dashboard')
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user, defaults={'home_city': request.POST.get('home_city', 'Prayagraj')})
            login(request, user); return redirect('dashboard')
        else:
            for error in form.errors.values(): messages.error(request, error)
    return render(request, 'register.html', {'form': UserCreationForm()})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user()); return redirect('dashboard')
        else: messages.error(request, "Invalid username or password.")
    return render(request, 'login.html', {'form': AuthenticationForm()})

def logout_view(request):
    logout(request); return redirect('index')



from django.http import JsonResponse

def search_suggestions(request):
    query = request.GET.get('term', '').strip()
    suggestions = []
    if query:
   
        res_list = Restaurant.objects.filter(name__icontains=query)[:5]
        suggestions = [res.name for res in res_list]
    return JsonResponse(suggestions, safe=False)
# DASHBOARD & MATCH SCORE
@login_required
def dashboard(request):

    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    
 
    selected_city = request.GET.get('city', user_profile.home_city or 'Prayagraj').strip()
    search = request.GET.get('q', '').strip()
    cuisine_filter = request.GET.get('cuisine', '').strip()


    if selected_city.lower() in ['allahabad', 'prayagraj']:
       
        city_res = Restaurant.objects.filter(
            Q(location__icontains='Allahabad') | Q(location__icontains='Prayagraj')
        )
    else:
      
        city_res = Restaurant.objects.filter(location__icontains=selected_city)

 
    if search:
    
        city_res = city_res.filter(
            Q(name__icontains=search) | 
            Q(cuisine__icontains=search) |
            Q(locality__icontains=search)
        )

    if cuisine_filter:
        city_res = city_res.filter(cuisine__icontains=cuisine_filter)

    results = []
    for res in city_res.order_by('-rating'):
        # 
        score = (res.rating * 10)
        res.match_score = int(min(score, 99))
        results.append(res)


    results = sorted(results, key=lambda x: x.match_score, reverse=True)


    context = {
        'results': results[:6],          
        'more_results': results[6:],     
        'cities': Restaurant.objects.values_list('location', flat=True).distinct().order_by('location'),
        'selected_city': selected_city,
        'notifications': Activity.objects.all().order_by('-created_at')[:10],
        'total_count': city_res.count()
    }
    
    return render(request, 'dashboard.html', context)
# RATING AVERAGE ENGINE
@login_required
def submit_rating(request, pk):
    if request.method == "POST":
        res = get_object_or_404(Restaurant, pk=pk)
        user_val = float(request.POST.get('user_rating', 0))
        if 1 <= user_val <= 5:
            # Average Calculation
            total = (res.rating * res.review_count) + user_val
            res.review_count += 1
            res.rating = round(total / res.review_count, 1)
            res.save()
            messages.success(request, f"Synced your {user_val}★ rating!")
    return redirect('restaurant_detail', pk=pk)

# DATA ACTIONS
@login_required
def add_restaurant(request):
    if request.method == "POST":
        res = Restaurant.objects.create(
            name=request.POST.get('name'), location=request.POST.get('location'),
            cuisine=f"{request.POST.get('diet_type')}, {request.POST.get('cuisine', '')}",
            locality=request.POST.get('locality'), phone=request.POST.get('phone'),
            rating=4.0, review_count=1, created_by=request.user
        )
        Activity.objects.create(user=request.user, message=f"🆕 Added {res.name}")
    return redirect('dashboard')

@login_required
def update_restaurant(request, pk):
    res = get_object_or_404(Restaurant, pk=pk)
    if request.method == "POST":
        res.locality = request.POST.get('locality'); res.phone = request.POST.get('phone')
        res.save(); messages.info(request, "Updated intelligence.")
    return redirect('restaurant_detail', pk=pk)

from django.http import HttpResponseForbidden 

@login_required
def delete_restaurant(request, pk):

    res = get_object_or_404(Restaurant, pk=pk)

    # user verification before deletion
    if res.created_by != request.user:
        return HttpResponseForbidden("Bhai, ye restaurant tumne add nahi kiya hai, toh tum ise delete nahi kar sakte!")

    # delete
    res.delete()
    
    # display essage
    messages.warning(request, f"Restaurant '{res.name}' has been removed.")
    
    return redirect('user_profile')

@login_required
def report_data(request, pk):
    res = get_object_or_404(Restaurant, pk=pk)
    Activity.objects.create(user=request.user, message=f"🚩 Flagged: {res.name}")
    return redirect('restaurant_detail', pk=pk)

# PROFILE & DISCOVERY
@login_required
def user_profile_view(request, username=None):
    # 1. यूजर को डेटाबेस से ढूंढना
    target_user = get_object_or_404(User, username=username) if username else request.user
    

    stats = Restaurant.objects.filter(created_by=target_user).values('cuisine').annotate(count=Count('id')).order_by('-count')[:5]
    
    # clean chart lables
    chart_labels = [s['cuisine'].split(',')[0].strip() for s in stats]
    chart_data = [s['count'] for s in stats]

    # user contributions
    my_restaurants = Restaurant.objects.filter(created_by=target_user).order_by('-id')
    
    # badge logic
    count = my_restaurants.count()
    badges = []
    if count >= 1: badges.append({'title': 'Contributor', 'icon': '🎯'})
    if count >= 5: badges.append({'title': 'Taste Maker', 'icon': '👨‍🍳'})
    if count >= 10: badges.append({'title': 'Pro Reviewer', 'icon': '🖋️'})
    if count >= 20: badges.append({'title': 'Legend', 'icon': '⭐'})


    context = {
        'target_user': target_user,
        'user_profile': Profile.objects.filter(user=target_user).first(),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'my_restaurants': my_restaurants,
        'total_added': count,
        'badges': badges,
        'is_owner': (request.user == target_user),
    }
    return render(request, 'my_profile.html', context)

@login_required
def update_profile(request):
    if request.method == "POST":
        p, _ = Profile.objects.get_or_create(user=request.user)
        p.home_city = request.POST.get('home_city'); p.save()
    return redirect('user_profile')

@login_required
def restaurant_detail(request, pk):
    res = get_object_or_404(Restaurant, pk=pk)
    return render(request, 'restaurant_detail.html', {'res': res})

@login_required
def discover_view(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    user_city = user_profile.home_city or 'Prayagraj'
    
    # Random restaurants for discovery
    res = Restaurant.objects.all().order_by('?')[:9] 
    
    return render(request, 'discover.html', {
        'results': res, 
        'city': user_city,  
    })
@login_required
def compare_view(request):
    return render(request, 'compare.html', {'all_res': Restaurant.objects.all()})


@login_required
def report_restaurant(request, pk):
    if request.method == 'POST':
        res = get_object_or_404(Restaurant, pk=pk)
        reason = request.POST.get('reason')
        
    
        Report.objects.create(
            restaurant=res,
            reported_by=request.user,
            reason=reason
        )
        
        messages.warning(request, "Thank you! Report submitted successfully.")
        return redirect('restaurant_detail', pk=pk)
    
@login_required
def community_chat(request):
    return render(request, 'community.html')