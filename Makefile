.PHONY: install test smoke regression contract negative e2e performance boundary report docker-test lint clean

install:
	pip install -r requirements-dev.txt

test:
	pytest -v --alluredir=allure-results

smoke:
	pytest -m smoke -v --alluredir=allure-results

regression:
	pytest -m regression -v --alluredir=allure-results

contract:
	pytest -m contract -v --alluredir=allure-results

negative:
	pytest -m negative -v --alluredir=allure-results

e2e:
	pytest -m e2e -v --alluredir=allure-results

performance:
	pytest -m performance -v --alluredir=allure-results

boundary:
	pytest -m boundary -v --alluredir=allure-results

report:
	allure serve allure-results

docker-test:
	docker-compose up --build api-tests

docker-smoke:
	docker-compose up --build smoke-tests

lint:
	flake8 api_clients/ config/ models/ tests/ utils/ --max-line-length=120
	black --check api_clients/ config/ models/ tests/ utils/
	isort --check-only api_clients/ config/ models/ tests/ utils/

format:
	black api_clients/ config/ models/ tests/ utils/
	isort api_clients/ config/ models/ tests/ utils/

clean:
	rm -rf allure-results/ allure-report/ __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
