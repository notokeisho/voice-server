"""Whisper.cpp server client for audio transcription."""

from pathlib import Path

import httpx

from app.config import settings


class WhisperError(Exception):
    """Base exception for whisper client errors."""

    pass


class WhisperServerError(WhisperError):
    """Raised when whisper server returns an error response."""

    pass


class WhisperTimeoutError(WhisperError):
    """Raised when whisper server request times out."""

    pass


class WhisperClient:
    """HTTP client for whisper.cpp server.

    This client communicates with a whisper.cpp server to transcribe
    audio files to text.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 60.0,
    ):
        """Initialize WhisperClient.

        Args:
            base_url: Base URL of the whisper server. Defaults to settings.
            timeout: Request timeout in seconds. Defaults to 60.
        """
        self.base_url = base_url or settings.whisper_server_url
        self.timeout = timeout

    async def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file to transcribe.

        Returns:
            The transcribed text.

        Raises:
            WhisperError: If the file is not found or connection fails.
            WhisperServerError: If the server returns an error response.
            WhisperTimeoutError: If the request times out.
        """
        # Check if file exists
        path = Path(audio_path)
        if not path.exists():
            raise WhisperError(f"Audio file not found: {audio_path}")

        # Read file and send to whisper server
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(audio_path, "rb") as f:
                    files = {"file": (path.name, f, "audio/wav")}
                    response = await client.post(
                        f"{self.base_url}/inference",
                        files=files,
                        data={"response_format": "json"},
                    )

                if response.status_code != 200:
                    raise WhisperServerError(
                        f"Whisper server error: {response.status_code} - {response.text}"
                    )

                result = response.json()
                return result.get("text", "")

        except httpx.TimeoutException as e:
            raise WhisperTimeoutError(f"Whisper server timeout: {e}") from e
        except httpx.ConnectError as e:
            raise WhisperError(f"Failed to connect to whisper server: {e}") from e
        except httpx.HTTPError as e:
            raise WhisperError(f"HTTP error: {e}") from e

    async def health_check(self) -> bool:
        """Check if the whisper server is healthy.

        Returns:
            True if the server is reachable, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False


# Default client instance
whisper_client = WhisperClient()
