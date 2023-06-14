from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
# from live import routing as live_routing
# from alert import routing as alert_routing
# from live.consumer import SendLearnerConsumer, LiveStatusConsumer

urlpatterns = []
# urlpatterns += live_routing.websocket_urlpatterns
# urlpatterns += alert_routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            urlpatterns
        )
    ),
    # 'channel': ChannelNameRouter({
    #     "send-learner": SendLearnerConsumer,
    #     "live-status": LiveStatusConsumer,
    # }),
})
