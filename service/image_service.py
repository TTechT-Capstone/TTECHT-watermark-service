# service/image_service.py
import os
import io
import base64
import binascii
from typing import Optional, Dict, Any
from PIL import Image as PILImage

# Try Cloudinary, but don't require it - use for local testing
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_OK = True
except Exception:
    CLOUDINARY_OK = False


class ImageService:
    """
    Uploads images either to Cloudinary (if available) or falls back to local storage.
    Public methods:
      - upload_base64_image(base64_string) -> dict
      - delete_image(public_id=None, local_path=None) -> bool
      - get_image_info(public_id=None, local_path=None) -> dict
    """

    def __init__(self):
        self.allowed_formats = ['jpeg', 'jpg', 'png', 'gif']
        self.max_file_size = 10 * 1024 * 1024  # 10MB in bytes
        # Local storage root (used when Cloudinary isn't configured)
        self.local_root = os.getenv("LOCAL_UPLOAD_ROOT", "./data/uploads")
        os.makedirs(self.local_root, exist_ok=True)

    # API Methods

    def upload_base64_image(self, base64_string: str) -> Dict[str, Any]:
        """
        Upload base64-encoded image.
        Returns:
          If Cloudinary configured: { public_id, url, width, height, format, file_size, created_at, storage:"cloudinary" }
          Else (local):              { path, width, height, format, file_size, storage:"local" }
        Raises:
          ValueError on validation errors; Exception on upload failures.
        """
        try:
            # Validate and decode
            image_data = self._validate_and_decode_base64(base64_string)

            # Validate image format and size
            meta = self._validate_image(image_data)

            # Try Cloudinary; otherwise save locally
            return self._upload_to_cloudinary_or_local(image_data, meta)

        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Image upload failed: {str(e)}")

    def delete_image(self, public_id: Optional[str] = None, local_path: Optional[str] = None) -> bool:
        """
        Delete an image by Cloudinary public_id or local_path.
        Returns True on success, False otherwise.
        """
        # Cloudinary path
        if public_id:
            if not (CLOUDINARY_OK and self._cloudinary_configured()):
                raise Exception("Cloudinary not configured; cannot delete by public_id.")
            try:
                result = cloudinary.uploader.destroy(public_id)
                return result.get('result') == 'ok'
            except Exception as e:
                raise Exception(f"Failed to delete image from Cloudinary: {str(e)}")

        # Local path
        if local_path:
            try:
                os.remove(local_path)
                return True
            except FileNotFoundError:
                return False
            except Exception as e:
                raise Exception(f"Failed to delete local image: {str(e)}")

        raise ValueError("Must provide either public_id (Cloudinary) or local_path (local file).")

    def get_image_info(self, public_id: Optional[str] = None, local_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get image information either from Cloudinary (public_id) or local file (local_path).
        Returns a dict with metadata.
        """
        # Cloudinary info
        if public_id:
            if not (CLOUDINARY_OK and self._cloudinary_configured()):
                raise Exception("Cloudinary not configured; cannot fetch info by public_id.")
            try:
                result = cloudinary.api.resource(public_id)
                return {
                    'public_id': result['public_id'],
                    'url': result['secure_url'],
                    'width': result.get('width'),
                    'height': result.get('height'),
                    'format': result.get('format'),
                    'file_size': result.get('bytes'),
                    'created_at': result.get('created_at'),
                    'storage': 'cloudinary'
                }
            except Exception as e:
                raise Exception(f"Failed to get image info from Cloudinary: {str(e)}")

        # Local info
        if local_path:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            try:
                with PILImage.open(local_path) as im:
                    im.load()
                    fmt = (im.format or "").lower()
                    width, height = im.size
                file_size = os.path.getsize(local_path)
                return {
                    'path': local_path,
                    'width': width,
                    'height': height,
                    'format': fmt,
                    'file_size': file_size,
                    'storage': 'local'
                }
            except Exception as e:
                raise Exception(f"Failed to read local image info: {str(e)}")

        raise ValueError("Must provide either public_id (Cloudinary) or local_path (local file).")

    # Helpers

    def _validate_and_decode_base64(self, base64_string: str) -> bytes:
        """Validate and decode a base64 string to raw bytes."""
        if not base64_string or not isinstance(base64_string, str):
            raise ValueError("Base64 string is required and must be a string")

        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:'):
                base64_string = base64_string.split(',', 1)[1]

            image_data = base64.b64decode(base64_string)
            if len(image_data) == 0:
                raise ValueError("Decoded image data is empty")
            return image_data

        except binascii.Error:
            raise ValueError("Invalid base64 string format")

    def _validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate image data, size, and format.
        Returns a dict with inferred format/size for convenience.
        """
        if len(image_data) > self.max_file_size:
            raise ValueError(f"Image size exceeds maximum allowed size of {self.max_file_size // (1024*1024)}MB")

        try:
            image_stream = io.BytesIO(image_data)
            with PILImage.open(image_stream) as pil_image:
                fmt = (pil_image.format or "").lower()
                if fmt not in self.allowed_formats:
                    raise ValueError(f"Unsupported image format: {pil_image.format}. "
                                     f"Allowed formats: {', '.join(self.allowed_formats)}")
                width, height = pil_image.size
                if width < 1 or height < 1:
                    raise ValueError("Invalid image dimensions")
                # Fully load to ensure data is valid
                pil_image.load()
                return {"format": fmt, "width": width, "height": height}
        except PILImage.UnidentifiedImageError:
            raise ValueError("Invalid image data or corrupted image")

    def _upload_to_cloudinary_or_local(self, image_data: bytes, meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Try Cloudinary upload; if not configured, save to local disk.
        """
        image_stream = io.BytesIO(image_data)

        if CLOUDINARY_OK and self._cloudinary_configured():
            try:
                upload_params = {
                    'folder': os.getenv('CLOUDINARY_UPLOAD_FOLDER', 'watermark_app/'),
                    'transformation': [{'width': 1024, 'crop': 'limit'}],
                    'resource_type': 'image',
                }
                result = cloudinary.uploader.upload(image_stream, **upload_params)
                return {
                    'public_id': result['public_id'],
                    'url': result['secure_url'],
                    'width': result.get('width', meta.get("width")),
                    'height': result.get('height', meta.get("height")),
                    'format': result.get('format', meta.get("format")),
                    'file_size': result.get('bytes'),
                    'created_at': result.get('created_at'),
                    'storage': 'cloudinary'
                }
            except Exception as e:
                # If Cloudinary fails, fall back to local save
                pass  # We'll continue to local path below

        # Local fallback
        os.makedirs(self.local_root, exist_ok=True)
        fname = f"local_{os.urandom(4).hex()}.{meta.get('format', 'jpg') or 'jpg'}"
        local_path = os.path.join(self.local_root, fname)
        try:
            with open(local_path, "wb") as f:
                f.write(image_stream.getvalue())
        except Exception as e:
            raise Exception(f"Local upload failed: {str(e)}")

        # compute size from bytes to be accurate
        file_size = os.path.getsize(local_path)
        return {
            'path': local_path,
            'width': meta.get("width"),
            'height': meta.get("height"),
            'format': meta.get("format"),
            'file_size': file_size,
            'storage': 'local'
        }

    def _cloudinary_configured(self) -> bool:
        # Minimal check: either CLOUDINARY_URL env or the trio of vars is set
        return bool(
            os.getenv('CLOUDINARY_URL')
            or (
                os.getenv('CLOUDINARY_CLOUD_NAME')
                and os.getenv('CLOUDINARY_API_KEY')
                and os.getenv('CLOUDINARY_API_SECRET')
            )
        )
