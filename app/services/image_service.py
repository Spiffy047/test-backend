import cloudinary
import cloudinary.uploader
from flask import current_app
from PIL import Image
import io
import base64

class ImageService:
    """Service for handling image uploads using Cloudinary"""
    
    @staticmethod
    def configure_cloudinary():
        """Configure Cloudinary with app settings"""
        cloudinary.config(
            cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
            api_key=current_app.config.get('CLOUDINARY_API_KEY'),
            api_secret=current_app.config.get('CLOUDINARY_API_SECRET')
        )
    
    @staticmethod
    def resize_image(image_data, max_width=800, max_height=600, quality=85):
        """Resize and optimize image before upload"""
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Calculate new dimensions maintaining aspect ratio
            width, height = image.size
            ratio = min(max_width/width, max_height/height)
            
            if ratio < 1:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            print(f"Error resizing image: {e}")
            return image_data
    
    @staticmethod
    def upload_image(image_data, folder="servicedesk", public_id=None):
        """Upload image to Cloudinary with optimization"""
        try:
            ImageService.configure_cloudinary()
            
            # Resize and optimize image
            optimized_image = ImageService.resize_image(image_data)
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                optimized_image,
                folder=folder,
                public_id=public_id,
                resource_type="image",
                format="jpg",
                quality="auto:good",
                fetch_format="auto"
            )
            
            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result['width'],
                'height': result['height'],
                'bytes': result['bytes']
            }
            
        except Exception as e:
            print(f"Error uploading image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def upload_base64_image(base64_string, folder="servicedesk", public_id=None):
        """Upload base64 encoded image"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64 to bytes
            image_data = base64.b64decode(base64_string)
            
            return ImageService.upload_image(image_data, folder, public_id)
            
        except Exception as e:
            print(f"Error uploading base64 image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_image(public_id):
        """Delete image from Cloudinary"""
        try:
            ImageService.configure_cloudinary()
            
            result = cloudinary.uploader.destroy(public_id)
            return result['result'] == 'ok'
            
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    @staticmethod
    def get_optimized_url(public_id, width=None, height=None, crop="fill"):
        """Get optimized image URL with transformations"""
        try:
            ImageService.configure_cloudinary()
            
            transformations = {
                'quality': 'auto:good',
                'fetch_format': 'auto'
            }
            
            if width:
                transformations['width'] = width
            if height:
                transformations['height'] = height
            if width or height:
                transformations['crop'] = crop
            
            url = cloudinary.CloudinaryImage(public_id).build_url(**transformations)
            return url
            
        except Exception as e:
            print(f"Error generating optimized URL: {e}")
            return None