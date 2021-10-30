import pytest
from django.urls import reverse
from companies.models import Company
import json


COMPANIES_URL = reverse("companies-list")
pytestmark = pytest.mark.django_db

# ---------------------------- Test GET companies ---------------------------- #


def test_zero_companies_should_return_empty_list(client) -> None:
    response = client.get(COMPANIES_URL)
    assert response.status_code == 200
    assert json.loads(response.content) == []


def test_one_company_exists_should_succeed(client) -> None:
    test_company: Company = Company.objects.create(name="Amazon")
    response = client.get(COMPANIES_URL)
    response_content = json.loads(response.content)[0]
    assert response.status_code == 200
    assert response_content.get("name") == test_company.name
    assert response_content.get("status") == test_company.status
    assert response_content.get("application_link") == test_company.application_link

    assert response_content.get("notes") == test_company.notes


# -------------------------- End Test GET companies -------------------------- #


# ---------------------------- Test POST companies --------------------------- #


def test_create_company_without_arguments_should_fail(client) -> None:
    response = client.post(path=COMPANIES_URL)
    response_content = json.loads(response.content)
    assert response.status_code == 400
    assert response_content == {"name": ["This field is required."]}


def test_create_existing_company_should_fail(client) -> None:
    apple = Company.objects.create(name="Apple")
    response = client.post(path=COMPANIES_URL, data={"name": "Apple"})
    response_content = json.loads(response.content)
    assert response.status_code == 400
    assert response_content == {"name": ["company with this name already exists."]}


def test_create_company_with_only_name_all_fields_should_be_default(client) -> None:
    response = client.post(path=COMPANIES_URL, data={"name": "Test Company"})
    assert response.status_code == 201
    response_content: dict = json.loads(response.content)
    assert response_content["status"] == "Hiring"
    assert response_content["application_link"] == ""
    assert response_content["notes"] == ""


def test_create_company_with_layoffs_should_succeed(client) -> None:
    response = client.post(
        path=COMPANIES_URL, data={"name": "Test Company", "status": "Layoffs"}
    )
    assert response.status_code == 201
    response_content: dict = json.loads(response.content)
    assert response_content["name"] == "Test Company"
    assert response_content["status"] == "Layoffs"
    assert response_content["application_link"] == ""
    assert response_content["notes"] == ""


def test_create_company_with_wrong_status_should_fail(client) -> None:
    response = client.post(
        path=COMPANIES_URL,
        data={"name": "Test Company", "status": "WrongStatus"},
    )
    assert (response.status_code, 400)
    assert "WrongStatus" in str(response.content)
    assert "is not a valid choice" in str(response.content)


# -------------------------- End Test POST companies ------------------------- #


@pytest.mark.xfail
def test_should_be_okay_if_fails() -> None:
    assert (1, 2)


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
