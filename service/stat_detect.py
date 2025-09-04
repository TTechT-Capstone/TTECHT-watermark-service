import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import json, os, shutil, uuid, time
from typing import Optional, Dict, Any
import base64
import io
from PIL import Image
import tempfile

class StatDetectService:
    def __init__(self):
        self.default_pcc_threshold = 0.70
        self.detections_root = os.path.join(tempfile.gettempdir(), "detections")
    
    def compare_watermarks_from_base64(self, original_wm_b64: str, extracted_wm_b64: str, 
                                      pcc_threshold: float = None, save_record: bool = False,
                                      suspect_image_b64: str = None) -> Dict[str, Any]:
        """
        Compare watermarks from base64 inputs and optionally save detection record
        
        Args:
            original_wm_b64: Base64 encoded original watermark image
            extracted_wm_b64: Base64 encoded extracted watermark image
            pcc_threshold: PCC threshold for detection (default: 0.70)
            save_record: Whether to save detection record for admin
            suspect_image_b64: Optional base64 encoded suspect image for record (ignored for core detection)
            
        Returns:
            Dict containing metrics, detection results, and optional record info
        """
        if pcc_threshold is None:
            pcc_threshold = self.default_pcc_threshold
        
        # Create temp directory for processing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Decode and save images temporarily (only required images for detection)
            original_path = self._save_base64_to_temp(original_wm_b64, temp_dir, "original_wm")
            extracted_path = self._save_base64_to_temp(extracted_wm_b64, temp_dir, "extracted_wm")
            
            # Skip suspect_image processing - not needed for detection
            
            # Compute metrics using your exact logic
            metrics = self._compute_metrics(original_path, extracted_path)
            
            # Determine if it's a match
            is_detected = self._is_match(metrics, pcc_threshold, use_abs=True)
            
            # Prepare result
            result = {
                "metrics": metrics,
                "detection": {
                    "is_match": is_detected,
                    "pcc_threshold": float(pcc_threshold),
                    "used_absolute_pcc": True
                },
                "comparison_results": {
                    "pcc": metrics["pcc"],
                    "pcc_abs": metrics["pcc_abs"],
                    "mse": metrics["mse"],
                    "ssim": metrics["ssim"],
                    "psnr": metrics["psnr"]
                }
            }
            
            # Save detection record if requested
            if save_record:
                record_result = self._save_detection_record(
                    original_logo_path=original_path,
                    extracted_wm_path=extracted_path,
                    metrics=metrics,
                    matched_json_path=None,
                    suspect_image_path=None,  # No longer processing suspect image
                    out_root=self.detections_root,
                    pcc_threshold=pcc_threshold
                )
                result["detection_record"] = {
                    "record_id": record_result["record"]["id"],
                    "record_dir": record_result["record_dir"],
                    "record_json": record_result["record_json"],
                    "created_at": record_result["record"]["created_at"]
                }
            
            return result
            
        finally:
            # Clean up temp files
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def _calculate_psnr(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate PSNR between two images"""
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        mse = np.mean((img1 - img2) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr

    def _pearson_correlation_coefficient(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Pearson Correlation Coefficient - main metric for unauthorized image usage detection"""
        img1 = img1.astype(np.float32)
        img2 = img2.astype(np.float32)
        numerator   = np.sum((img1 - np.mean(img1)) * (img2 - np.mean(img2)))
        denominator = np.sqrt(np.sum((img1 - np.mean(img1)) ** 2) * np.sum((img2 - np.mean(img2)) ** 2))
        return float(numerator / denominator) if denominator != 0 else 0.0

    def _mean_squared_error(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Mean Squared Error"""
        return float(np.mean((img1 - img2) ** 2))

    def _compute_metrics(self, original_path: str, extracted_path: str) -> Dict[str, float]:
        """
        Returns a dict with PCC, PCC absolute value, MSE, SSIM, PSNR.
        Resizes extracted to match original if needed.
        """
        original  = cv2.imread(original_path,  cv2.IMREAD_GRAYSCALE)
        extracted = cv2.imread(extracted_path, cv2.IMREAD_GRAYSCALE)
        if original is None or extracted is None:
            raise FileNotFoundError("One or both image files could not be read.")

        if original.shape != extracted.shape:
            extracted = cv2.resize(extracted, (original.shape[1], original.shape[0]))

        pcc_val  = self._pearson_correlation_coefficient(original, extracted)
        mse_val  = self._mean_squared_error(original, extracted)
        ssim_val = ssim(original, extracted)
        psnr_val = self._calculate_psnr(original, extracted)

        return {
            "pcc":     float(pcc_val),
            # This will be used to compare with the threshold
            "pcc_abs": float(abs(pcc_val)),   
            "mse":     float(mse_val),
            "ssim":    float(ssim_val),
            "psnr":    float(psnr_val)
        }

    def _is_match(self, metrics: Dict[str, float], pcc_threshold: float = 0.70, use_abs: bool = True) -> bool:
        """Convenience: decide using PCC or |PCC|."""
        key = "pcc_abs" if use_abs else "pcc"
        return float(metrics.get(key, 0.0)) >= float(pcc_threshold)

    def _save_detection_record(self,
        original_logo_path: str,
        extracted_wm_path: str,
        metrics: Dict[str, float],
        matched_json_path: Optional[str] = None,
        suspect_image_path: Optional[str] = None,
        out_root: str = "./detections",
        pcc_threshold: float = 0.70
    ) -> Dict[str, object]:
        """
        Saves a folder with:
          - record.json (metrics + thresholds + paths + timestamps)
          - original_logo.(png/jpg)
          - extracted_wm.(png/jpg)
          - suspect.(png/jpg)          [optional if provided]
          - sideinfo.wm.json           [optional copy if provided]
        Returns a dict with 'record_dir', 'record_json', and 'record'.
        """
        rec_id  = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        rec_dir = os.path.join(out_root, rec_id)
        os.makedirs(rec_dir, exist_ok=True)

        def _copy(src: Optional[str], name: str) -> Optional[str]:
            if src and os.path.exists(src):
                ext = os.path.splitext(src)[1].lower()
                dst = os.path.join(rec_dir, name + ext)
                shutil.copy2(src, dst)
                return dst
            return None

        paths = {
            "original_logo": _copy(original_logo_path, "original_logo"),
            "extracted_wm":  _copy(extracted_wm_path,  "extracted_wm"),
            "suspect":       _copy(suspect_image_path, "suspect") if suspect_image_path else None,
            "sideinfo_json": _copy(matched_json_path,  "sideinfo") if matched_json_path else None,
        }

        record = {
            "id": rec_id,
            "created_at": int(time.time()),
            "metrics": metrics,
            # ** We have to clarified why we using absolute value for PCC 
            "thresholds": {"pcc_abs": float(pcc_threshold)},        
            "passed": bool(float(metrics.get("pcc_abs", 0.0)) >= float(pcc_threshold)),
            "paths": paths
        }

        rec_json = os.path.join(rec_dir, "record.json")
        with open(rec_json, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        return {"record_dir": rec_dir, "record_json": rec_json, "record": record}

    def _save_base64_to_temp(self, base64_string: str, temp_dir: str, filename: str) -> str:
        """Save base64 image to temporary file and return path"""
        if not base64_string or not isinstance(base64_string, str):
            raise ValueError("Base64 string is required and must be a string")
        
        # Remove data URL prefix if present
        if base64_string.startswith('data:'):
            base64_string = base64_string.split(',')[1]
        
        # Basic validation - check if string looks like base64
        if len(base64_string.strip()) == 0:
            raise ValueError("Base64 string is empty after processing")
        
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
        
        # Check if decoded data has reasonable size for an image
        if len(image_data) < 100:  # Very small, likely not a real image
            raise ValueError(f"Decoded image data too small ({len(image_data)} bytes), likely not a valid image")
        
        # Convert to PIL Image to determine format
        image_stream = io.BytesIO(image_data)
        try:
            pil_image = Image.open(image_stream)
            # Verify image can be processed
            pil_image.verify()
            # Re-open for actual use (verify() closes the image)
            image_stream.seek(0)
            pil_image = Image.open(image_stream)
        except Exception as e:
            # Provide more detailed error information
            data_preview = image_data[:50] if len(image_data) > 50 else image_data
            raise ValueError(f"Invalid image data: {str(e)}. Data length: {len(image_data)} bytes. The base64 data does not represent a valid image file.")
        
        # Determine file extension
        format_lower = pil_image.format.lower() if pil_image.format else 'jpg'
        ext = '.jpg' if format_lower == 'jpeg' else f'.{format_lower}'
        
        # Save to temp file
        temp_path = os.path.join(temp_dir, f"{filename}{ext}")
        pil_image.save(temp_path)
        
        return temp_path
    
    # Compare watermarks using multiple metrics (for Test case)
    def compare_watermarks(self, original_path: str, extracted_path: str) -> Dict[str, float]:
        """
        Compare watermarks and print results (original console output functionality)
        Returns the computed metrics dict
        """
        original  = cv2.imread(original_path,  cv2.IMREAD_GRAYSCALE)
        extracted = cv2.imread(extracted_path, cv2.IMREAD_GRAYSCALE)

        if original is None or extracted is None:
            raise FileNotFoundError("One or both image files could not be read. Please check the paths again.")

        if original.shape != extracted.shape:
            extracted = cv2.resize(extracted, (original.shape[1], original.shape[0]))

        pcc        = self._pearson_correlation_coefficient(original, extracted)
        mse_val    = self._mean_squared_error(original, extracted)
        ssim_val   = ssim(original, extracted)
        psnr_score = self._calculate_psnr(original, extracted)

        print("PCC:", pcc)
        # We use the absolute value of PCC for detection since there are some extracted watermark that have reversed colors
        print("|PCC|:", abs(pcc))
        print("MSE:", mse_val)
        print("SSIM:", ssim_val)
        print("PSNR:", psnr_score, "dB")
        
        return {
            "pcc": float(pcc),
            "pcc_abs": float(abs(pcc)),
            "mse": float(mse_val),
            "ssim": float(ssim_val),
            "psnr": float(psnr_score)
        }
