from channels.routing import route, include

channel_routing = [
    include('index.routing.channel_routing', path=r'^/'),
]
