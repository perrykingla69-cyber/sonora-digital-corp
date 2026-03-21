.PHONY: api-dev api-v2 test-backend frontend-install frontend-dev

api-dev:
	python backend/main.py

api-v2:
	uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000

test-backend:
	python -m pytest tests/ -v

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev
