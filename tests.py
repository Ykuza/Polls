import datetime
from .models import Question, Choice
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

# Create your tests here.

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and pulished the
    given number of `days` offset to now(negative for questions
    published in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question_text, days, choice_text=0):
    """
    Createing a question and choice with giver informations
    """
    question = create_question(question_text, days)
    if choice_text:
        question.choice_set.create(choice_text=choice_text, votes=0)
        return question
    else:
        return question

class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() will return False 
        for questions whose pub-date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() will return False 
        if their pub_date is older than one day.
        """
        time = timezone.now() + datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() will return True 
        if the pub_date of the question is withn a day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestioinIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        if no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future arent displayedon the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if blth past and future questions exist, only past questions are displayed.
        """
        question = create_question(question_text="Past question_future.", days=-30)
        create_question(question_text="Future question_past.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question1.", days=-30)
        question2 = create_question(question_text="Past question2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_choice(choice_text='Choice', question_text="Future question.", days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_choice(choice_text='Choice' , question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_no_choice_question(self):
        """
        The question without any choice will not be displayed on detail view.
        """
        no_choice_question = create_choice(question_text="No Choice Question", days=-2)
        url = reverse('polls:detail', args=(no_choice_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class QuestionResultViewTests(TestCase):
    def test_future_question(self):
        """
        The result view of a question with a pub-date in the future
        returns a 404 not found.
        """
        future_question = create_choice(question_text="Future Question.", days=5,
        choice_text="future Question")
        url = reverse('polls:result', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results of a question with past pub_date will be displayed.
        """
        past_question = create_choice(question_text='Past Question.', days=-5,
        choice_text='Past Question')
        url = reverse('polls:result', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_no_choice(self):
        """
        Will rise a 404 not found if the question hadnt any choice.
        """
        no_choice = create_choice(question_text="No Choice.", days=-2)
        url = reverse('polls:result', args=(no_choice.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_with_choice(self):
        """
        Will show the choice_text if thers was some.
        """
        question = create_choice(question_text='With Choice.', days=-2, 
        choice_text='With Choice')
        url = reverse('polls:result', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
