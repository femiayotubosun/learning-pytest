import json
from django.test import TestCase, Client
from django.urls import reverse
from companies.models import Company


class CompaniesApiSetUp(TestCase):
    def setUp(self) -> None:
        self.client: Client = Client()
        self.companies_url = reverse("companies-list")

    def tearDown(self) -> None:
        pass


class TestGetCompanies(CompaniesApiSetUp):
    def test_zero_companies_should_return_empty_list(self) -> None:
        response = self.client.get(self.companies_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_one_company_exists_should_succeed(self) -> None:
        test_company: Company = Company.objects.create(name="Amazon")
        response = self.client.get(self.companies_url)
        response_content = json.loads(response.content)[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content.get("name"), test_company.name)
        self.assertEqual(response_content.get("status"), test_company.status)
        self.assertEqual(
            response_content.get("application_link"), test_company.application_link
        )
        self.assertEqual(response_content.get("notes"), test_company.notes)

        test_company.delete()
