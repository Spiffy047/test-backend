import os
import cloudinary
import cloudinary.uploader

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
    
    def upload_image(self, file, ticket_id, user_id):
        try:
            # Reset file pointer
            file.seek(0)
            
            # Upload directly without PIL processing to avoid dependency issues
            result = cloudinary.uploader.upload(
                file,
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