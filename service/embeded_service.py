from tqdm import tqdm
from PIL import Image
import numpy as np
import cv2
import pywt                    
import json, os
from pathlib import Path
import base64
import io
import tempfile
from typing import Tuple, Dict, Any

class EmbeddedService:
    def __init__(self):
        self.wavelet_name = "haar"  # Wavelet type for DWT
        self.alpha = 0.6  # Default scaling factor
    
    def embed_watermark_from_base64(self, original_image_b64: str, watermark_image_b64: str, 
                                   alpha: float = None, output_dir: str = None) -> Dict[str, Any]:
        """
        Embed watermark into original image using base64 inputs
        
        Args:
            original_image_b64: Base64 encoded original image
            watermark_image_b64: Base64 encoded watermark image
            alpha: Scaling factor for watermark embedding (default: 0.6)
            output_dir: Output directory for watermarked image (default: temp directory)
            
        Returns:
            Dict containing watermarked image info and metadata
        """
        if alpha is None:
            alpha = self.alpha
            
        # Decode base64 images
        original_image = self._decode_base64_to_pil(original_image_b64)
        watermark_image = self._decode_base64_to_pil(watermark_image_b64)
        
        # Convert to RGB if needed
        original_image = original_image.convert("RGB")
        watermark_image = watermark_image.convert("RGB")
        
        # Resize watermark to match original image size
        watermark_image = watermark_image.resize(original_image.size)
        
        # Split the image into three color channels → numpy float64
        orig_r, orig_g, orig_b = [np.float64(c) for c in original_image.split()]
        watermark_r, watermark_g, watermark_b = [np.float64(c) for c in watermark_image.split()]
        
        # Embed watermark in each channel
        watermark_r_modifier, S_val_R, LL_shape_R = self._embed_watermark_channel(orig_r, watermark_r, alpha, "Red")
        watermark_g_modifier, S_val_G, LL_shape_G = self._embed_watermark_channel(orig_g, watermark_g, alpha, "Green")
        watermark_b_modifier, S_val_B, LL_shape_B = self._embed_watermark_channel(orig_b, watermark_b, alpha, "Blue")
        
        # Normalize back to 0-255 uint8
        orig_r8 = self._normalize_uint8(watermark_r_modifier)
        orig_g8 = self._normalize_uint8(watermark_g_modifier)
        orig_b8 = self._normalize_uint8(watermark_b_modifier)
        
        # Merge channels back to RGB image
        watermarked_rgb = Image.merge("RGB",
                                      (Image.fromarray(orig_r8),
                                       Image.fromarray(orig_g8),
                                       Image.fromarray(orig_b8)))
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = os.path.join(tempfile.gettempdir(), "watermarked_images")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        unique_id = str(uuid.uuid4())
        out_path = os.path.join(output_dir, f"watermarked_{unique_id}.jpg")
        
        # Save the watermarked image
        watermarked_rgb.save(out_path)
        
        # Create metadata
        meta = {
            "wm_params": { 
                "alpha": float(alpha), 
                "wavelet": self.wavelet_name, 
                "channels": "RGB" 
            },
            "canonical_size": list(watermarked_rgb.size),
            "output_path": out_path,
            "ll_shapes": { 
                "R": list(LL_shape_R), 
                "G": list(LL_shape_G), 
                "B": list(LL_shape_B) 
            },
            "host_S": {
                "R": [float(x) for x in S_val_R.tolist()],
                "G": [float(x) for x in S_val_G.tolist()],
                "B": [float(x) for x in S_val_B.tolist()]
            },
            "watermark_ref": {
                "resized_to": list(original_image.size)
            }
        }
        
        # Save metadata to JSON file
        meta_path = os.path.splitext(out_path)[0] + ".wm.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        # Convert watermarked image to base64 for API response
        watermarked_b64 = self._pil_to_base64(watermarked_rgb)
        
        return {
            "watermarked_image_b64": watermarked_b64,
            "output_path": out_path,
            "metadata_path": meta_path,
            "metadata": meta,
            "image_size": watermarked_rgb.size,
            "unique_id": unique_id
        }
    
    def _embed_watermark_channel(self, orig_channel: np.ndarray, wm_channel: np.ndarray, 
                                alpha: float, cname: str) -> Tuple[np.ndarray, np.ndarray, Tuple]:
        """
        Embed the watermark image (watermark_channel) into orig_channel (single color plane)
        Here we are using 1-level Haar DWT + SVD on the LL sub-band.
        """
        with tqdm(total=100,
                  desc=f"Embedding in {cname} channel",
                  bar_format="{l_bar}{bar} [ time left: {remaining} ]") as pbar:

            # Implement DWT algorithm on the original and watermark channels
            LL_orig, (LH_orig, HL_orig, HH_orig) = pywt.dwt2(orig_channel, self.wavelet_name) # LL is the low-frequency sub-band -> Highest embedded quality
            LL_wm, (LH_wm, HL_wm, HH_wm) = pywt.dwt2(wm_channel, self.wavelet_name)
            pbar.update(25)

            # Implement SVD algorithm on LL sub-bands
            U_orig, S_orig, V_orig = np.linalg.svd(LL_orig, full_matrices=False)
            U_wm, S_wm, V_wm = np.linalg.svd(LL_wm, full_matrices=False)
            pbar.update(25)

            # Embedding the watermark
            S_modifier = S_orig + alpha * S_wm
            LL_modifier = (U_orig @ np.diag(S_modifier) @ V_orig)
            pbar.update(25)

            # Reconstruct the modified channel using Inverse DWT
            coeffs_modifier = (LL_modifier, (LH_orig, HL_orig, HH_orig))
            watermarked_channel = pywt.idwt2(coeffs_modifier, self.wavelet_name)
            pbar.update(25)

        return watermarked_channel, S_orig, LL_orig.shape
    
    def _normalize_uint8(self, mat: np.ndarray) -> np.ndarray:
        """Normalize matrix back to 0-255 uint8"""
        mat = cv2.normalize(mat, None, 0, 255, cv2.NORM_MINMAX)
        return mat.astype(np.uint8)
    
    def _decode_base64_to_pil(self, base64_string: str) -> Image.Image:
        """Decode base64 string to PIL Image"""
        # Remove data URL prefix if present
        if base64_string.startswith('data:'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 with padding handling
        try:
            # Try direct decode first
            image_data = base64.b64decode(base64_string)
        except Exception:
            # If that fails, try with padding
            try:
                # Add padding if needed
                padding = 4 - (len(base64_string) % 4)
                if padding != 4:
                    base64_string += '=' * padding
                image_data = base64.b64decode(base64_string)
            except Exception as e:
                raise ValueError(f"Invalid base64 format: {str(e)}")
        
        # Convert to PIL Image
        image_stream = io.BytesIO(image_data)
        return Image.open(image_stream)
    
    def _pil_to_base64(self, pil_image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        img_data = buffer.getvalue()
        return base64.b64encode(img_data).decode('utf-8')
