import asyncio

import log
from sanic import Sanic, response
from sanic_openapi import doc

from app import helpers, settings, utils

app = Sanic(name="memegen")
helpers.configure(app)


@app.get("/")
@doc.exclude(True)
def index(request):
    return response.json(
        {
            "templates": request.app.url_for("templates.index", _external=True),
            "images": request.app.url_for("images.index", _external=True),
            "docs": request.app.url_for("swagger.index", _external=True),
        }
    )


@app.get("/examples")
@doc.exclude(True)
async def examples(request):
    examples = await asyncio.to_thread(helpers.get_example_images, request)
    urls = [example[0] for example in examples]
    refresh = "debug" in request.args and settings.DEBUG
    content = utils.html.gallery(urls, columns=True, refresh=refresh)
    return response.html(content)


@app.get("/test")
@doc.exclude(True)
async def test(request):
    if not settings.DEBUG:
        return response.redirect("/")
    urls = await asyncio.to_thread(helpers.get_test_images, request)
    content = utils.html.gallery(urls, columns=False, refresh=True)
    return response.html(content)


@app.get("/favicon.ico")
@doc.exclude(True)
async def favicon(request):
    return await response.file("app/static/favicon.ico")


if __name__ == "__main__":
    log.reset()
    log.silence("datafiles", allow_warning=True)
    app.run(
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS,
        debug=settings.DEBUG,
        access_log=False,
    )
