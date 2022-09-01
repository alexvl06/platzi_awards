from datetime import  timedelta
from django.utils import timezone
from django.test import TestCase
from .models import Question
from django.urls.base import reverse

class QuestionModeltests(TestCase):
    def test_was_published_recently_with_future_questions(self):
        """was_published_recently returns False for quesions whose pub-date is in the future"""
        time = timezone.now()+timedelta(days=30)
        future_question = Question(question_text= "¿Quién es el mejor Course Director de Platzi?",pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

def create_question(question_text, days):
    """
        Create a question with the given "question_text" and publication date parameters, the last one has the given number of offset days until now. 
        (Negative for questions published in the past and positive for questions that are going to be published in the future)
    """
    time = timezone.now()+timedelta(days=days)
    return Question.objects.create(question_text= question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """If no question exist, an appropiate  messsage is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_question(self):
        """Questions with a public date in the future areen't displayed on the index page"""
        create_question("funture question", days= 1)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Questions with a public date in the past aree displayed on the index page"""
        question = create_question("past question", days= -1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """Even if both past and future question exist, only past questions are displayed"""
        create_question(question_text = "Past question", days= 1)
        past_question = create_question(question_text = "Past question", days= -1)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question])

    def test_two_past_questions(self):
        """ The questions index page can display multiple questions"""
        past_question1 = create_question(question_text = "Past question 1", days= -1)
        past_question2 = create_question(question_text = "Past question 2", days= -2)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [past_question1, past_question2])

class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
            The detail view of a question with a pub_date in the future should return a 404 error not found.
        """
        future_question = create_question(question_text = "Past question 1", days= 1)
        url  = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        """
            The detail view of a question with a pub_date in the past should display the question details.
        """
        past_question = create_question(question_text = "Past question 1", days= -1)
        url  = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)