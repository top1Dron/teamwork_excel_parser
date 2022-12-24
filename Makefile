SERVER = uvicorn

PORT=8002


# ##########################################################################
# common commands

run:
	$(SERVER) main:app --host 127.0.0.1 --port $(PORT) --reload --lifespan on

install:
	pip install -r requirements.txt
