from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve
from django.template.loader import render_to_string
from lists.views import home_page
from lists.models import Item, List


# class ItemModelTest(TestCase):
#     def test_saving_and_retrieving_items(self):
#         first_item = Item()
#         first_item.text = 'The first list item'
#         first_item.save()
#
#         second_item = Item()
#         second_item.text = 'Item the second'
#         second_item.save()
#
#         saved_items = Item.objects.all()
#         self.assertEqual(saved_items.count(), 2)
#
#         first_saved_item = saved_items[0]
#         second_saved_item = saved_items[1]
#         self.assertEqual(first_saved_item.text, 'The first list item')
#         self.assertEqual(second_saved_item.text, 'Item the second')


class HomePageTest(TestCase):
    # def test_root_url_resolves_to_home_page_view(self):
    #     found = resolve('/')
    #     self.assertEqual(found.func, home_page)

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    # def test_only_saves_items_when_necessary(self):
    #     self.client.get('/')
    #     self.assertEqual(Item.objects.count(), 0)

    def test_home_page_return_correct_html(self):
        request = HttpRequest()  # (1)
        response = home_page(request)  # (2)
        html = response.content.decode('utf8')  # (3)
        self.assertTrue(html.startswith('<html>'))  # (4)
        self.assertIn('<title>To-Do lists</title>', html)
        self.assertTrue(html.endswith('</html>'))  # (4)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_user = List.objects.create()
        response = self.client.get(f'/lists/{list_user.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        # Item.objects.create(text='itemey 1')
        # Item.objects.create(text='itemey 2')
        # response = self.client.get('/lists/the-new-page/')
        # self.assertContains(response, 'itemey 1')
        # self.assertContains(response, 'itemey 2')
        corrtect_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=corrtect_list)
        Item.objects.create(text='itemey 2', list=corrtect_list)
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{corrtect_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        corrtect_list = List.objects.create()
        response = self.client.get(f'/lists/{corrtect_list.id}/')
        self.assertEqual(response.context['list'], corrtect_list)

class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')
        # self.assertIn('A new list item', response.content.decode())
        # self.assertTemplateUsed(response, 'home.html')
        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(response['location'], '/')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        new_list = List.objects.first()
        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(response['location'], '/lists/the-new-page/')
        self.assertRedirects(response, f'/lists/{new_list.id}/')

class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        corrtect_list = List.objects.create()

        self.client.post(
            f'/lists/{corrtect_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, corrtect_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        corrtect_list = List.objects.create()
        response = self.client.post(
            f'/lists/{corrtect_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )
        self.assertRedirects(response, f'/lists/{corrtect_list.id}/')