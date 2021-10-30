from unittest import TestCase
import pytest
from django.http import response
from django.test import Client, client
from django.urls import reverse
from companies.models import Company
import json


# --------------------------------- Test Case -------------------------------- #
@pytest.mark.django_db
class BasicCompanyApiTestCase(TestCase):
    def setUp(self) -> None:
        self.client: Client = Client()
        self.companies_url = reverse("companies-list")

    def tearDown(self) -> None:
        pass


class TestGetCompanies(BasicCompanyApiTestCase):
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


class TestPostCompanies(BasicCompanyApiTestCase):
    def test_create_company_without_arguments_should_fail(self) -> None:
        response = self.client.post(path=self.companies_url)
        response_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_content, {"name": ["This field is required."]})

    def test_create_existing_company_should_fail(self) -> None:
        apple = Company.objects.create(name="Apple")
        response = self.client.post(path=self.companies_url, data={"name": "Apple"})
        response_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response_content, {"name": ["company with this name already exists."]}
        )

    def test_create_company_with_only_name_all_fields_should_be_default(self) -> None:
        response = self.client.post(
            path=self.companies_url, data={"name": "Test Company"}
        )
        self.assertEqual(response.status_code, 201)
        response_content: dict = json.loads(response.content)
        self.assertEqual(response_content["status"], "Hiring")
        self.assertEqual(response_content["application_link"], "")
        self.assertEqual(response_content["notes"], "")

    def test_create_company_with_layoffs_should_succeed(self) -> None:
        response = self.client.post(
            path=self.companies_url, data={"name": "Test Company", "status": "Layoffs"}
        )
        self.assertEqual(response.status_code, 201)
        response_content: dict = json.loads(response.content)
        self.assertEqual(response_content["name"], "Test Company")
        self.assertEqual(response_content["status"], "Layoffs")
        self.assertEqual(response_content["application_link"], "")
        self.assertEqual(response_content["notes"], "")

    def test_create_company_with_wrong_status_should_fail(self) -> None:
        response = self.client.post(
            path=self.companies_url,
            data={"name": "Test Company", "status": "WrongStatus"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("WrongStatus", str(response.content))
        print(str(response.content))
        self.assertIn("is not a valid choice", str(response.content))

    @pytest.mark.xfail
    def test_should_be_okay_if_fails(self) -> None:
        self.assertEqual(1, 2)


def raise_covid19_exception() -> None:
    raise ValueError("Coronavirus Exception")


def test_raise_covid19_exception_should_pass() -> None:
    with pytest.raises(ValueError) as e:
        raise_covid19_exception()
    assert "Coronavirus Exception" == str(e.value)


import logging

logger = logging.getLogger("CORONO_LOGS")


def function_that_logs_something() -> None:
    try:
        raise ValueError("Coronavirus Exception")
    except ValueError as e:
        logger.warning(f"I am logging {str(e)}")


def test_logged_warning_level(caplog) -> None:
    function_that_logs_something()
    assert "I am logging Coronavirus Exception" in caplog.text


def test_logged_info_level(caplog) -> None:
    with caplog.at_level(logging.INFO):
        logger.info("I am logging info level")
        assert "I am logging info level" in caplog.text
