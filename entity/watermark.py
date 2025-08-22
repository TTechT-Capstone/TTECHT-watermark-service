class Watermark:
    def __init__(self, watermark_id: int, store_name: str, watermark_url_image: str):
        """
        Watermark entity class
        
        Args:
            watermark_id: Unique identifier for the watermark (not null)
            store_name: Name of the store/brand associated with the watermark
            watermark_url_image: URL or path to the watermark image
        """
        self.watermark_id = watermark_id
        self.store_name = store_name
        self.watermark_url_image = watermark_url_image
    
    def to_dict(self) -> dict:
        """Convert watermark object to dictionary"""
        return {
            'watermark_id': self.watermark_id,
            'store_name': self.store_name,
            'watermark_url_image': self.watermark_url_image
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Watermark':
        """Create watermark object from dictionary"""
        return cls(
            watermark_id=data['watermark_id'],
            store_name=data['store_name'],
            watermark_url_image=data['watermark_url_image']
        )
    
    def __str__(self) -> str:
        return f"Watermark(id={self.watermark_id}, store='{self.store_name}', image='{self.watermark_url_image}')"
    
    def __repr__(self) -> str:
        return self.__str__()
