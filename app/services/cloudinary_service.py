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
            # Test configuration first
            cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
            api_key = os.environ.get('CLOUDINARY_API_KEY')
            api_secret = os.environ.get('CLOUDINARY_API_SECRET')
            
            if not all([cloud_name, api_key, api_secret]):
                print(f"Missing Cloudinary config: cloud_name={bool(cloud_name)}, api_key={bool(api_key)}, api_secret={bool(api_secret)}")
                return None
            
            # Reset file pointer
            file.seek(0)
            
            # Simple upload without transformations
            result = cloudinary.uploader.upload(
                file,
                folder=f"servicedesk/tickets/{ticket_id}",
                public_id=f"attachment_{user_id}_{ticket_id}"
            )
            
            return {
                'url': result['secure_url'],
                'public_id': result['public_id'],
                'width': result.get('width', 0),
                'height': result.get('height', 0),
                'format': result.get('format', 'unknown'),
                'bytes': result.get('bytes', 0)
            }
            
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_image(self, public_id):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result['result'] == 'ok'
        except Exception as e:
            print(f"Cloudinary delete error: {e}")
            return False