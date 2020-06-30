import json
from datetime import datetime as dt
from aiohttp import web


def count_comments(post_id):
    with open('comments.json', 'r') as file:
        data = json.load(file)
        comments = data['comments']
        matches = [comment for comment in comments if str(comment['post_id']) == str(post_id)]
        return matches


def prepare_json(data):
    posts = [{'id': p['id'],
              'title': p['title'],
              'date': p['date'],
              'body': p['body'],
              'comments': len(count_comments(p['id']))}
             for p in data['posts'] if p['deleted'] is False and dt.strptime(p['date'], "%Y-%m-%dT%H:%M:%S") < dt.now()]

    posts.sort(key=lambda post: dt.strptime(post['date'], "%Y-%m-%dT%H:%M:%S").timestamp())
    return {'posts': posts}


def find_post(id):
    with open('posts.json', 'r') as file:
        data = json.load(file)
        posts = [{'id': p['id'],
                  'title': p['title'],
                  'date': p['date'],
                  'body': p['body'],
                  'comments': sorted(count_comments(p['id']), key=lambda comment: comment['date'])}
                 for p in data['posts'] if str(p['id']) == id and dt.strptime(p['date'], "%Y-%m-%dT%H:%M:%S") < dt.now() and not p['deleted']]
        return posts


routes = web.RouteTableDef()


@routes.get('/')
async def get_handler(request):
    with open('posts.json', 'r') as file:
        data = json.load(file)
        result = prepare_json(data)
        result['post_count'] = len(result['posts'])
        return web.json_response(result)


@routes.get('/post/{id}')
async def variable_handler(request):
    posts = find_post(request.match_info['id'])
    if len(posts) == 0:
        raise web.HTTPNotFound
    else:
        post = posts[0]
        post['comment_count'] = len(post['comments'])
        return web.json_response(post)


app = web.Application()
app.add_routes(routes)


if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
