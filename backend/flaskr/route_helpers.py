from flask import Flask, abort, jsonify, Response, Request


def get_pagination(request: Request, PAGE_SIZE=10) -> tuple[int, int, int]:
        page = request.args.get("page", default=1, type=int)

        if page < 1:
            abort(400, description="page must be >= 1")

        offset = (page - 1) * PAGE_SIZE
        return page, PAGE_SIZE, offset