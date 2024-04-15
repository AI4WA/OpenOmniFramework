from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authenticate.utils.get_logger import get_logger
from chat.models import Chat, ChatRecord
from chat.serializers import RespondToChatSerializer

logger = get_logger(__name__)


class ChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a chat which need to be responded",
        responses={200: "Chat get successfully", 404: "No chat found"},
    )
    @action(detail=False, methods=["get"])
    def get_chat(self, request):
        # get all chats
        # TODO: it is not efficient to do it this way.
        chats = Chat.objects.all().order_by("-created_at")
        # get the first chat that needs a response
        for chat in chats:
            needed, messages = chat.action_required()
            if needed:
                return Response(
                    {
                        "messages": messages,
                        "llm_model_name": chat.llm_model_name,
                        "uuid": chat.uuid,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"message": "No chat found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @swagger_auto_schema(
        operation_description="Respond to a chat",
        responses={200: "Chat responded successfully", 404: "No chat found"},
        request_body=RespondToChatSerializer,
    )
    @action(detail=False, methods=["post"])
    def respond(self, request):
        serializer = RespondToChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        chat_uuid = serializer.validated_data.get("chat_uuid")
        message = serializer.validated_data.get("message")
        chat = Chat.objects.filter(uuid=chat_uuid)
        if not chat.exists():
            return Response(
                {"message": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        chat = chat.first()
        chat.respond(message)
        return Response(
            {"message": "Chat responded successfully"},
            status=status.HTTP_200_OK,
        )

    # get a summary task
    @swagger_auto_schema(
        operation_description="Get a chat which need to be summarized",
        responses={200: "Chat get successfully", 404: "No chat found"},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="summarize_chat",
        url_name="summarize_chat",
    )
    def get_summary_chat(self, request):
        # get all chats without summary or summary is ""
        chats = Chat.objects.filter(summary__isnull=True).order_by("-created_at")
        chats_empty = Chat.objects.filter(summary="").order_by("-created_at")
        chats = chats.union(chats_empty)
        for chat in chats:
            needed, prompt = chat.summary_required()
            if needed:
                return Response(
                    {
                        "prompt": prompt,
                        "llm_model_name": chat.llm_model_name,
                        "uuid": chat.uuid,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"message": "No chat found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # respond to a summary task
    @swagger_auto_schema(
        operation_description="Summarize a chat",
        responses={200: "Chat summarized successfully", 404: "No chat found"},
        request_body=RespondToChatSerializer,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="update_summarize_chat",
        url_name="post_summarize_chat",
    )
    def post_summarize_chat(self, request):
        serializer = RespondToChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        chat_uuid = serializer.validated_data.get("chat_uuid")
        message = serializer.validated_data.get("message")
        chat = Chat.objects.filter(uuid=chat_uuid)
        if not chat.exists():
            return Response(
                {"message": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        chat = chat.first()
        if message is None:
            # chat summary will be the first three words in the prompt
            record = (
                ChatRecord.objects.filter(chat=chat, role="user")
                .order_by("-created_at")
                .first()
            )
            chat.summary = " ".join(record.message.split()[:3])
        else:
            # if the message is too long, get the first 10 words
            chat.summary = " ".join(message.split()[:10])
            chat.summary = message
        chat.save()
        return Response(
            {"message": "Chat summarized successfully"},
            status=status.HTTP_200_OK,
        )
