from fastapi import FastAPI

app = FastAPI()


def get_asgi_application():
    return app
