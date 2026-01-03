from django.shortcuts import render, get_object_or_404

# from django.template import loader
# from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

# pylint: disable=no-member


# Create your views here.
# def index(request):
#     #   return HttpResponse("Hello, world. You're at the polls index.")
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     #  output = ", ".join([q.question_text for q in latest_question_list])
#     #  return HttpResponse(output)
#     # template = loader.get_template("polls/index.html")
#     context = {"latest_question_list": latest_question_list}
#     # return HttpResponse(template.render(context, request))
#     return render(request, "polls/index.html", context=context)


class IndexView(generic.ListView):
    # model = Question
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to
        be published in the future).
        """
        # return Question.objects.order_by("-pub_date")[:5]
        # return Question.objects.filter(pub_date__lte=timezone.now())\
        # .order_by("-pub_date")[:5]
        return (
            Question.objects.filter(pub_date__lte=timezone.now())
            .filter(choice__isnull=False)
            .distinct()
            .order_by("-pub_date")[:5]
        )
        # Why .distinct()?
        # Because one question with multiple choices would otherwise appear multiple times.


# def detail(request, question_id):
#     # return HttpResponse("You're looking at question %s" % question_id)
#     # try:
#     # question = Question.objects.get(pk=question_id)
#     # except Question.DoesNotExist:
#     # raise Http404("Question does not exist")
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/detail.html", {"question": question})


class DetailView(generic.DetailView):
    # model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """Exclude any quesions that aren't published yet."""
        # return Question.objects.filter(pub_date__lte=timezone.now())
        return (
            Question.objects.filter(choice__isnull=False)
            .distinct()
            .filter(pub_date__lte=timezone.now())
        )


# def results(request, question_id):
#     # response = "You're looking at the results of question %s"
#     # return HttpResponse(response % question_id)
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/results.html", context={"question": question})


class ResultsView(generic.DetailView):
    # model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """Exclude any questions that aren't published yet."""
        # return Question.objects.filter(pub_date__lte=timezone.now())
        return (
            Question.objects.filter(choice__isnull=False)
            .distinct()
            .filter(pub_date__lte=timezone.now())
        )


def vote(request, question_id):
    # return HttpResponse("You're voting on question %s" % question_id)
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def create_question(request):
    """Shows a form to enter a question."""
    if request.method == "GET":
        return render(
                request,
                "polls/create.html",
        )
    else:
        try:
            question_text = request.POST["q"]
            if question_text == "":
                raise ValueError
        # except (KeyError, Question.DoesNotExist):
        except (ValueError):
            return render(
                request,
                "polls/create.html",
                {"error_message": "Please enter a valid question."},
            )
    # else:
        question = Question.objects.create(question_text=question_text, pub_date=timezone.now())
        question.save()
        # return HttpResponseRedirect(reverse("polls:index"))
        return HttpResponseRedirect(reverse("polls:index"))
