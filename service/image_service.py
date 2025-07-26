# service/image_service.py
import cloudinary.uploader
import cloudinary.api
import base64
import binascii
import io
import os
from PIL import Image as PILImage

class ImageService:
    def __init__(self):
        self.allowed_formats = ['jpeg', 'jpg', 'png', 'gif']
        self.max_file_size = 10 * 1024 * 1024  # 10MB in bytes

    def upload_base64_image(self, base64_string: str) -> dict:
        """
        Upload base64 encoded image to Cloudinary
        
        Args:
            base64_string: Base64 encoded image string
            
        Returns:
            dict: Cloudinary response with image URL and metadata
            
        Raises:
            ValueError: If validation fails
            Exception: If upload fails
        """
        try:
            # Validate and process base64 string
            image_data = self._validate_and_decode_base64(base64_string)
            
            # Validate image format and size
            self._validate_image(image_data)
            
            # Upload to Cloudinary and return result
            return self._upload_to_cloudinary(image_data)
            
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Image upload failed: {str(e)}")

    def _validate_and_decode_base64(self, base64_string: str) -> bytes:
        """Validate and decode base64 string"""
        if not base64_string or not isinstance(base64_string, str):
            raise ValueError("Base64 string is required and must be a string")
        
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            if len(image_data) == 0:
                raise ValueError("Decoded image data is empty")
                
            return image_data
            
        except binascii.Error:
            raise ValueError("Invalid base64 string format")

    def _validate_image(self, image_data: bytes) -> None:
        """Validate image format and size"""
        # Check file size
        if len(image_data) > self.max_file_size:
            raise ValueError(f"Image size exceeds maximum allowed size of {self.max_file_size // (1024*1024)}MB")
        
        try:
            # Validate image format using PIL
            image_stream = io.BytesIO(image_data)
            with PILImage.open(image_stream) as pil_image:
                if pil_image.format.lower() not in self.allowed_formats:
                    raise ValueError(f"Unsupported image format: {pil_image.format}. Allowed formats: {', '.join(self.allowed_formats)}")
                
                # Check image dimensions (optional)
                if pil_image.width < 1 or pil_image.height < 1:
                    raise ValueError("Invalid image dimensions")
                    
        except PILImage.UnidentifiedImageError:
            raise ValueError("Invalid image data or corrupted image")

    def _upload_to_cloudinary(self, image_data: bytes) -> dict:
        """Upload image to Cloudinary and return formatted response"""
        try:
            image_stream = io.BytesIO(image_data)
            
            upload_params = {
                'folder': os.getenv('CLOUDINARY_UPLOAD_FOLDER', 'watermark_app/'),
                'transformation': [{'width': 1024, 'crop': 'limit'}],
                'resource_type': 'image'
            }
            
            result = cloudinary.uploader.upload(image_stream, **upload_params)
            
            # Return formatted response
            return {
                'public_id': result['public_id'],
                'url': result['secure_url'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'file_size': result.get('bytes'),
                'created_at': result.get('created_at')
            }
            
        except Exception as e:
            raise Exception(f"Cloudinary upload failed: {str(e)}")

    def delete_image(self, public_id: str) -> bool:
        """
        Delete image from Cloudinary
        
        Args:
            public_id: Cloudinary public ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
            
        except Exception as e:
            raise Exception(f"Failed to delete image: {str(e)}")

    def get_image_info(self, public_id: str) -> dict:
        """
        Get image information from Cloudinary
        
        Args:
            public_id: Cloudinary public ID
            
        Returns:
            dict: Image information
        """
        try:
            result = cloudinary.api.resource(public_id)
            
            return {
                'public_id': result['public_id'],
                'url': result['secure_url'],
                'width': result.get('width'),
                'height': result.get('height'),
                'format': result.get('format'),
                'file_size': result.get('bytes'),
                'created_at': result.get('created_at')
            }
            
        except Exception as e:
            raise Exception(f"Failed to get image info: {str(e)}")