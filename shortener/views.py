from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from shortener.models import ShortURL
from shortener.serializers import ShortURLAnalyticsSerializer, ShortURLSerializer


class ShortenURLCreateView(CreateAPIView):
    """
    POST /api/shorten/
    Accepts {"original_url": "<url>"} and returns the persisted
    ShortURL representation, including the derived short_url.
    """

    queryset = ShortURL.objects.all()
    serializer_class = ShortURLSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class URLRedirectView(APIView):
    """
    GET /r/<short_code>/
    Performs a 302 redirect to the original URL, atomically incrementing
    the click counter and stamping last_accessed on every hit.
    Returns a 404 for unknown short codes.
    """

    def get(self, request, short_code, *args, **kwargs):
        short_url = get_object_or_404(ShortURL, short_code=short_code)
        short_url.register_click()
        return HttpResponseRedirect(short_url.original_url)


class URLAnalyticsView(RetrieveAPIView):
    """
    GET /api/analytics/<short_code>/
    Returns click counts, original URL, short code, and timestamps
    for the given short code. Returns a 404 for unknown short codes.
    """

    queryset = ShortURL.objects.all()
    serializer_class = ShortURLAnalyticsSerializer
    lookup_field = "short_code"
    lookup_url_kwarg = "short_code"


def home_view(request):
    """
    GET /
    Renders the minimal interactive frontend UI.
    """
    return render(request, "index.html")