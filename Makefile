.PHONY: install dev stop logs

BACKEND_DIR := backend
FRONTEND_DIR := frontend
BACKEND_PID := .backend.pid
FRONTEND_PID := .frontend.pid

# ── Install ────────────────────────────────────────────────────────────────────

install:
	@echo "→ Installing backend dependencies..."
	cd $(BACKEND_DIR) && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt -q
	@echo "→ Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "✓ Done. Run 'make dev' to start."

# ── Dev ───────────────────────────────────────────────────────────────────────

dev: stop
	@echo "→ Starting backend on http://localhost:8000"
	@cd $(BACKEND_DIR) && ./venv/bin/uvicorn main:app --reload --port 8000 > ../.backend.log 2>&1 & echo $$! > ../$(BACKEND_PID)
	@echo "→ Starting frontend on http://localhost:3000"
	@cd $(FRONTEND_DIR) && npm run dev > ../.frontend.log 2>&1 & echo $$! > ../$(FRONTEND_PID)
	@sleep 2
	@echo ""
	@echo "  Backend  → http://localhost:8000"
	@echo "  Frontend → http://localhost:3000"
	@echo ""
	@echo "  make logs   — stream logs"
	@echo "  make stop   — stop both"

# ── Stop ──────────────────────────────────────────────────────────────────────

stop:
	@if [ -f $(BACKEND_PID) ]; then \
		kill $$(cat $(BACKEND_PID)) 2>/dev/null && echo "→ Backend stopped" || true; \
		rm -f $(BACKEND_PID); \
	fi
	@if [ -f $(FRONTEND_PID) ]; then \
		kill $$(cat $(FRONTEND_PID)) 2>/dev/null && echo "→ Frontend stopped" || true; \
		rm -f $(FRONTEND_PID); \
	fi
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# ── Logs ──────────────────────────────────────────────────────────────────────

logs:
	@tail -f .backend.log .frontend.log
