import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# pylint: disable=no-member


# Create your tests here.
class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is
        olderder than one day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is
        within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=22, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertTrue(recent_question.was_published_recently())


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text, votes):
    """Create a choice for a given question. Used to create choices for questions
    in tests below because list 'latest_question_list' filters out questions with
    no choices."""
    question.choice_set.create(choice_text=choice_text, votes=votes)


class QuestionIndexViewTests(TestCase):
    """ Tests for view IndexView. """
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question", days=-30)
        create_choice(question, "test_choice", 0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        question = create_question(question_text="Future question", days=30)
        create_choice(question, "test_choice", 0)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_and_past_question(self):
        """
        Even if both future and past questions exist, only past questions are displayed.
        """
        question1 = create_question(question_text="Past question", days=-30)
        create_choice(question1, "test_choice_1", 0)
        question2 = create_question(question_text="Future questions", days=30)
        create_choice(question2, "test_choice_2", 0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question1],
        )
        
    def test_question_has_no_choices(self):
        """If a question has not choices it is not displayed."""
        create_question(question_text="Question with no choices", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [],
        )
        

    def test_two_past_questions(self):
        """The question index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1", days=-30)
        create_choice(question1, "test_choice", 0)
        question2 = create_question(question_text="Past question 2", days=-5)
        create_choice(question2, "test_choice", 0)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    """ Tests for view DetailView. """
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future returns
        a 404 not found.
        """
        future_question = create_question(question_text="Future question", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """ 
        The detail view of a question with a pub_date in the past 
        displays the question's text.
        """
        past_question = create_question(question_text="Past question", days=-5)
        create_choice(past_question, "test_choice_2", 0)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        
    def test_question_without_choice(self):
        """ A question that has no choices is not displayed by the detail view. """
        question = create_question(question_text="Past question with no choice", days=-5)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
class QuestionResultView(TestCase):
    """ Tests for view ResultView. """
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question", days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """
        The results view of a question wich is published in the past
        (pub_date in the past) displays the question's text.
        """
        past_question = create_question(question_text="Past question", days=-5)
        create_choice(past_question, "test_choice", 0)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        
    def test_question_without_choice(self):
        """ A question that has no choices is not displayed by the results view. """
        question = create_question(question_text="Past question with no choice", days=-5)
        url = reverse('polls:results', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)