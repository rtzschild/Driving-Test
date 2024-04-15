"""
Author:
Susan Wagle
"""
import datetime
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

from .models import *
from django.urls import reverse
from Quiz.forms import UserRegistrationForm, UserLoginForm


# method for logging in a user
def loginUser(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # Redirect to next page if user requested
                next_url = request.POST.get('next', '/')
                if next_url:
                    return redirect(next_url)
                response = HttpResponseRedirect(reverse('index'))
                return response
            # error message if the username or password is incorrect
            messages.error(request, 'Invalid Credentials. Please try again.')
            return render(request, 'login.html', {
                'form': form,
                'user': None
            })
        else:
            messages.error(request, 'Error Occured. Please try again.')
            return render(request, 'login.html', {
                'form': form
            })

    form = UserLoginForm()
    # Checking if user is authenticated or not
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html', {'form': form, 'user': None})


# method of logout user
def logoutUser(request):
    logout(request)
    return redirect('/login')


# Method for registration new user
def register(request):
    # Checking if user is authenticated or not
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if User.objects.filter(email=email).exists():
                messages.error(
                    request, 'Email already exists. Please choose unique email.')

                return render(request, 'register.html', {
                    'form': form,
                    'user': None
                })
            new_user = User.objects.create_user(
                username=username, email=email, password=password)
            new_user.save()
            # Directly login after successful register
            login(request, new_user)
            return redirect('/')
        else:
            # defining error condition in the form
            if 'password' in form.errors:
                messages.error(
                    request, 'Password must be at least 8 characters long and contain letters, symbols and numbers.')
            elif 'username' in form.errors:
                messages.error(
                    request, 'Username already exists. Please choose another username.')
            elif 'email' in form.errors:
                messages.error(
                    request, 'Invalid Email. Please try again.')
            else:
                messages.error(
                    request, 'Error Occured. Please try again.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


# Method for displaying the index page
@login_required(login_url="/login")  # Middleware to authenticate user
def index(request):
    context = {'categories': Category.objects.all(),
               'user': request.user.username}
    if request.GET.get('category'):
        return redirect(f"/quiz?category={request.GET.get('category')}")
    return render(request, 'index.html', context)


# Method to start the quiz
@login_required(login_url="/login")  # Middleware to authenticate user
def quiz(request):
    questions = get_quiz(request)
    return render(request, 'quiz.html', {'questions': questions, 'user': request.user.username})


# Method to fetch quiz questions
@login_required(login_url="/login")  # Middleware to authenticate user
def get_quiz(request):
    # fetch all the objects
    question_objs = (Question.objects.all())
    try:
        # fetch according to the category
        category = request.GET.get('category')
        if not category:
            return redirect('/')
        question_objs = question_objs.filter(
            category__category_name__icontains=request.GET.get('category'))

        question_objs = list(question_objs)
        data = []
        # shuffle the questions
        random.shuffle(question_objs)
        for question_obj in question_objs:
            data.append({
                "id": question_obj.id,
                "category": question_obj.category.category_name,
                "question": question_obj.question,
                "marks": question_obj.marks,
                "answers": question_obj.get_answer()
            })
            # calculate the length of the number of question and display only 5 question
        if len(question_objs) >= 5:
            return random.sample(data, 5)
        else:
            # display if the length is small than 5
            return random.sample(data, len(question_objs))
    except ValueError:
        return render(request, 'quiz.html')


# Method to display the score
@login_required(login_url="/login")  # Middleware to authenticate user
def score(request):
    try:
        # filter according to the user name
        quiz_results = QuizResult.objects.filter(
            user__username__icontains=request.user)
        obj = {}
        for el in quiz_results:
            category = el.category

            if category in obj:
                obj[category].append(el)
            else:
                obj[category] = [el]

        # calculating scores by category
        scores = list()
        for el in obj.items():
            key, val = el
            highest = total_score = 0
            lowest = val[0].score
            count = len(val)
            for v in val:
                if highest < v.score:
                    highest = v.score
                if lowest > v.score:
                    lowest = v.score
                total_score += v.score
            scores.append({'category': key, 'total_score': total_score,
                           'count': count, 'highest': highest, 'lowest': lowest,
                           'average': round(float(total_score / count), 2)})

        context = {'user': request.user.username,
                   'quiz_results': quiz_results, 'scores': scores}
        return render(request, 'score.html', context)
    except ZeroDivisionError:
        return render(request, 'score.html')


# Method for displaying quiz result
@login_required(login_url="/login")  # Middleware to authenticate user
def result(request):
    if request.method == 'POST':
        user_answers = request.POST.dict()
        user_score = 0

        for question_id, selected_choice_id in user_answers.items():
            if question_id.startswith('question'):
                question = Question.objects.get(
                    pk=int(question_id[8:]))
                try:
                    category_identifier = question.category.category_name
                    category_instance = Category.objects.get(
                        category_name=category_identifier)
                    user12 = User.objects.get(
                        username=request.user)
                except (Category.DoesNotExist or User.DoesNotExist):
                    return redirect('/')

                selected_choice = Answer.objects.get(
                    pk=int(selected_choice_id))
                if selected_choice.is_correct:
                    user_score += 1
        current_date = datetime.now()
        # Create a new quiz result
        quiz_result = QuizResult(
            user=user12, score=user_score, category=category_instance)
        quiz_result.save()
        percentage = user_score / 5 * 100
        return render(request, 'quiz_result.html',
                      {'user_score': user_score, 'current_datetime': current_date, 'user': request.user.username,
                       'percentage': percentage, 'category_name': category_instance.category_name})
    return redirect('quiz')


def redirect_to_home(request):  # Redirects all other URLs to the home page
    return redirect('/')
