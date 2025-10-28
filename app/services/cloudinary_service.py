import os
import cloudinary
import cloudinary.uploader
from PIL import Image
import io

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
    
    def upload_image(self, file, ticket_id, user_id):
        try:
            # Resize image before upload
            image = Image.open(file)
            
            # Resize if larger than 1200px width
            if image.width > 1200:
                ratio = 1200 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((1200, new_height), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                img_byte_arr,
                folder=f"servicedesk/tickets/{ticket_id}",
                public_id=f"attachment_{user_id}_{ticket_id}",
                resource_type="image",
                transformation=[
                    {'width': 800, 'height': 600, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result['width'],
                'height': result['height'],
                'format': result['format'],
                'bytes': result['bytes']
            }
            
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            return None
    
    def delete_image(self, public_id):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result['result'] == 'ok'
        except Exception as e:
            print(f"Cloudinary delete error: {e}")
            return False