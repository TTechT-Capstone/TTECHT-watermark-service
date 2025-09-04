from tqdm import tqdm
from PIL import Image
import numpy as np
import cv2
import pywt
import os, json
from pathlib import Path
import glob
import base64
import io
import tempfile
from typing import Dict, Any, Tuple, Optional, Callable
import uuid
import requests

class ExtractService:
    def __init__(self, sideinfo_fetcher: Optional[Callable[[str], Optional[Dict[str, Any]]]] = None):
        self.phash_hamming_threshold = 12  # Hamming distance threshold for pHash (tune 8–14)
        self.sideinfo_dir = os.path.join(tempfile.gettempdir(), "watermarked_images")
        # Optional hook to fetch sideinfo JSON from an external database by key/id
        # Signature: fetcher(ref: str) -> Optional[dict]
        self.sideinfo_fetcher = sideinfo_fetcher
    
    def extract_watermark_from_base64(self, suspect_image_b64: str, sideinfo_json_path: str = None, 
                                     output_dir: str = None) -> Dict[str, Any]:
        """
        Extract watermark from suspect image using base64 input
        
        Args:
            suspect_image_b64: Base64 encoded suspect image
            sideinfo_json_path: Optional path/URL/DB-key to sideinfo JSON
            output_dir: Output directory for extracted watermark (default: temp directory)
            
        Returns:
            Dict containing extraction results and metadata
        """
        # Decode base64 image and save temporarily
        suspect_image = self._decode_base64_to_pil(suspect_image_b64)
        
        # Create temp directory for processing
        temp_dir = tempfile.mkdtemp()
        suspect_path = os.path.join(temp_dir, f"suspect_{uuid.uuid4().hex}.jpg")
        suspect_image.save(suspect_path)
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = os.path.join(tempfile.gettempdir(), "extracted_watermarks")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename for extracted watermark
        unique_id = str(uuid.uuid4())
        extracted_path = os.path.join(output_dir, f"extracted_{unique_id}.jpg")
        
        # Perform extraction (with optional sideinfo resolution)
        if sideinfo_json_path:
            meta, sideinfo_used = self._resolve_sideinfo(sideinfo_json_path)
            if meta is None:
                result = {"status": "skip_bad_meta", "reason": "Side-info not found/invalid. Proceed to embedding."}
            else:
                result = self._extract_from_suspect_with_meta(suspect_path, meta, extracted_path, sideinfo_used)
        else:
            result = self._extract_from_suspect(suspect_path, None, extracted_path)
        
        # Clean up temp file
        try:
            os.remove(suspect_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        # Convert extracted image to base64 if extraction was successful
        if result["status"] == "ok_extracted" and os.path.exists(extracted_path):
            with open(extracted_path, "rb") as f:
                extracted_b64 = base64.b64encode(f.read()).decode('utf-8')
            result["extracted_image_b64"] = extracted_b64
            result["unique_id"] = unique_id
        
        return result
    
    def extract_watermark_from_base64_with_json(self, suspect_image_b64: str, sideinfo_json: dict = None, 
                                               output_dir: str = None) -> Dict[str, Any]:
        """
        Extract watermark from suspect image using base64 input and JSON sideinfo
        
        Args:
            suspect_image_b64: Base64 encoded suspect image
            sideinfo_json: Optional JSON object with sideinfo data (instead of file path)
            output_dir: Output directory for extracted watermark (default: temp directory)
            
        Returns:
            Dict containing extraction results and metadata
        """
        # Decode base64 image and save temporarily
        suspect_image = self._decode_base64_to_pil(suspect_image_b64)
        
        # Create temp directory for processing
        temp_dir = tempfile.mkdtemp()
        suspect_path = os.path.join(temp_dir, f"suspect_{uuid.uuid4().hex}.jpg")
        suspect_image.save(suspect_path)
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = os.path.join(tempfile.gettempdir(), "extracted_watermarks")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename for extracted watermark
        unique_id = str(uuid.uuid4())
        extracted_path = os.path.join(output_dir, f"extracted_{unique_id}.jpg")
        
        # Perform extraction with JSON sideinfo
        if sideinfo_json:
            result = self._extract_from_suspect_with_meta(suspect_path, sideinfo_json, extracted_path, "provided_json")
        else:
            result = self._extract_from_suspect(suspect_path, None, extracted_path)
        
        # Clean up temp file
        try:
            os.remove(suspect_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        # Convert extracted image to base64 if extraction was successful
        if result["status"] == "ok_extracted" and os.path.exists(extracted_path):
            with open(extracted_path, "rb") as f:
                extracted_b64 = base64.b64encode(f.read()).decode('utf-8')
            result["extracted_image_b64"] = extracted_b64
            result["unique_id"] = unique_id
        
        return result
    
    def extract_watermark_from_url(self, suspect_image_url: str, sideinfo_json_path: str = None,
                                   output_dir: str = None, timeout_seconds: int = 15) -> Dict[str, Any]:
        """
        Extract watermark from a suspect image available at a URL
        
        Args:
            suspect_image_url: Publicly accessible HTTP(S) URL to the suspect image
            sideinfo_json_path: Optional path/URL/DB-key to sideinfo JSON
            output_dir: Output directory for extracted watermark (default: temp directory)
            timeout_seconds: HTTP timeout for fetching the image
        Returns:
            Dict containing extraction results and metadata
        """
        # Download image to PIL
        suspect_image = self._download_image_to_pil(suspect_image_url, timeout_seconds)
        
        # Create temp directory for processing
        temp_dir = tempfile.mkdtemp()
        suspect_path = os.path.join(temp_dir, f"suspect_{uuid.uuid4().hex}.jpg")
        suspect_image.save(suspect_path)
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = os.path.join(tempfile.gettempdir(), "extracted_watermarks")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename for extracted watermark
        unique_id = str(uuid.uuid4())
        extracted_path = os.path.join(output_dir, f"extracted_{unique_id}.jpg")
        
        # Perform extraction (with optional sideinfo resolution)
        if sideinfo_json_path:
            meta, sideinfo_used = self._resolve_sideinfo(sideinfo_json_path)
            if meta is None:
                result = {"status": "skip_bad_meta", "reason": "Side-info not found/invalid. Proceed to embedding."}
            else:
                result = self._extract_from_suspect_with_meta(suspect_path, meta, extracted_path, sideinfo_used)
        else:
            result = self._extract_from_suspect(suspect_path, None, extracted_path)
        
        # Clean up temp file
        try:
            os.remove(suspect_path)
            os.rmdir(temp_dir)
        except:
            pass
        
        # Convert extracted image to base64 if extraction was successful
        if result["status"] == "ok_extracted" and os.path.exists(extracted_path):
            with open(extracted_path, "rb") as f:
                extracted_b64 = base64.b64encode(f.read()).decode('utf-8')
            result["extracted_image_b64"] = extracted_b64
            result["unique_id"] = unique_id
        
        # Include the URL for traceability
        result["suspect_image_url"] = suspect_image_url
        return result
    
    def _to_uint8(self, mat: np.ndarray) -> np.ndarray:
        """Convert matrix to uint8 format"""
        mat = cv2.normalize(mat, None, 0, 255, cv2.NORM_MINMAX)
        return mat.astype(np.uint8)
    
    def _phash64_from_pil(self, img_pil: Image.Image) -> str:
        """Simple 64-bit pHash via DCT(32x32 gray)."""
        g = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2GRAY)
        g = cv2.resize(g, (32, 32), interpolation=cv2.INTER_AREA)
        dct = cv2.dct(np.float32(g))
        low = dct[:8, :8]
        med = np.median(low[1:].ravel())  # skip DC
        bits = (low > med).astype(np.uint8).ravel()[:64]
        val = 0
        for b in bits:
            val = (val << 1) | int(b)
        return f"{val:016x}"

    def _hamming64(self, h1: str, h2: str) -> int:
        """Calculate Hamming distance between two 64-bit hashes"""
        return bin(int(h1, 16) ^ int(h2, 16)).count("1")

    def _compute_image_phash(self, img_path: str) -> Optional[str]:
        """Compute perceptual hash for an image"""
        try:
            im = Image.open(img_path).convert("RGB")
            return self._phash64_from_pil(im)
        except Exception:
            return None

    def _load_sideinfo_candidates(self, dir_path: str):
        """Yield (json_path, meta_dict)."""
        for jp in glob.glob(os.path.join(dir_path, "*.wm.json")):
            try:
                with open(jp, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                yield jp, meta
            except Exception:
                continue

    def _find_best_sideinfo_for_suspect(self, suspect_image_path: str, dir_path: str = None, 
                                       max_ham: int = None) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Returns (best_json_path, best_meta) if a close match is found by pHash,
        else (None, None). Uses meta['output_path'] when present to hash the
        published watermarked image; otherwise derives image path from the json name.
        """
        if dir_path is None:
            dir_path = self.sideinfo_dir
        if max_ham is None:
            max_ham = self.phash_hamming_threshold
            
        try:
            suspect_hash = self._phash64_from_pil(Image.open(suspect_image_path).convert("RGB"))
        except Exception:
            return None, None

        best_json, best_meta, best_dist = None, None, 1_000

        for json_path, meta in self._load_sideinfo_candidates(dir_path):
            out_path = meta.get("output_path", "")
            if not out_path or not os.path.exists(out_path):
                # derive: change .wm.json -> .jpg/.png if possible
                stem = os.path.splitext(json_path)[0]
                for ext in (".jpg", ".jpeg", ".png"):
                    cand = stem + ext
                    if os.path.exists(cand):
                        out_path = cand
                        break
            if not out_path or not os.path.exists(out_path):
                continue

            cand_hash = self._compute_image_phash(out_path)
            if cand_hash is None:
                continue

            d = self._hamming64(suspect_hash, cand_hash)
            if d < best_dist:
                best_json, best_meta, best_dist = json_path, meta, d

        if best_json and best_dist <= max_ham:
            return best_json, best_meta
        return None, None
    
    def _resolve_sideinfo(self, ref: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Resolve sideinfo reference from file path, HTTP(S) URL, or database via fetcher.
        Returns (meta_dict, sideinfo_used_label)."""
        # 1) Local file path
        if isinstance(ref, str) and os.path.exists(ref):
            try:
                with open(ref, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                return meta, ref
            except Exception:
                return None, None
        # 2) HTTP(S) URL returning JSON
        if isinstance(ref, str) and ref.lower().startswith(("http://", "https://")):
            try:
                r = requests.get(ref, timeout=15)
                r.raise_for_status()
                return r.json(), ref
            except Exception:
                return None, None
        # 3) External DB via fetcher (e.g., pass an ID/key)
        if self.sideinfo_fetcher is not None:
            try:
                meta = self.sideinfo_fetcher(ref)
                if isinstance(meta, dict):
                    return meta, f"db:{ref}"
            except Exception:
                return None, None
        return None, None

    def _download_image_to_pil(self, url: str, timeout_seconds: int) -> Image.Image:
        """Download an image from URL into a PIL Image with basic validations."""
        if not url or not isinstance(url, str):
            raise ValueError("suspect_image_url must be a non-empty string URL")
        resp = requests.get(url, stream=True, timeout=timeout_seconds)
        resp.raise_for_status()
        content_type = resp.headers.get('Content-Type', '').lower()
        if 'image' not in content_type:
            # Fallback: still try to open if content-type is missing or wrong
            pass
        data = resp.content
        try:
            return Image.open(io.BytesIO(data)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Failed to decode image from URL: {e}")

    def _extract_channel(self, suspect_channel: np.ndarray, watermark_channel: np.ndarray, 
                        S_orig_saved: np.ndarray, wavelet_name: str, alpha: float = 0.6, 
                        cname: str = "") -> np.ndarray:
        """
        Semi-blind extraction using saved S_orig (from .wm.json).
        Includes length guards so slight size differences never crash.
        """
        with tqdm(total=100,
                  desc=f"Extracting {cname} channel",
                  bar_format="{l_bar}{bar} [ time left: {remaining} ]") as pbar:

            # DWTs
            LL_mod, (LHm, HLm, HHm)       = pywt.dwt2(suspect_channel,   wavelet_name)
            LL_wmref, (LH_wm, HL_wm, HH_wm) = pywt.dwt2(watermark_channel, wavelet_name)
            pbar.update(30)

            # SVDs
            U_mod, S_mod, V_mod = np.linalg.svd(LL_mod,   full_matrices=False)
            U_wm,  S_wm,  V_wm  = np.linalg.svd(LL_wmref, full_matrices=False)
            pbar.update(50)

            # Length guard (avoid crashes on off-by-1 sizes)
            n = min(len(S_mod), len(S_orig_saved), len(S_wm))
            if n == 0:
                # If nothing usable; return a zero channel to keep pipeline active
                return np.zeros_like(suspect_channel, dtype=np.float64)

            S_mod       = S_mod[:n]
            S_orig_used = S_orig_saved[:n]
            U_wm        = U_wm[:, :n]
            V_wm        = V_wm[:n, :]

            # Semi-blind extraction
            S_wm_est  = (S_mod - S_orig_used) / max(alpha, 1e-12)
            LL_wm_est = U_wm @ np.diag(S_wm_est) @ V_wm
            pbar.update(10)

            wm_coeffs      = (LL_wm_est, (LH_wm, HL_wm, HH_wm))
            wm_channel_est = pywt.idwt2(wm_coeffs, wavelet_name)
            pbar.update(10)

        return wm_channel_est

    def _extract_from_suspect(self, suspect_path: str, sideinfo_path: str, out_path: str) -> Dict[str, Any]:
        """
        Returns dict with:
          - status: "ok_extracted" | "skip_no_sideinfo" | "skip_bad_meta"
          - reason: present for skip_* statuses
          - extracted_path, alpha, wavelet, canonical_size, sideinfo_used, watermark_logo (on success)
        """
        # Auto-pick a sideinfo if not provided
        if not sideinfo_path:
            auto_json, auto_meta = self._find_best_sideinfo_for_suspect(suspect_path, self.sideinfo_dir, self.phash_hamming_threshold)
            if auto_json:
                sideinfo_path = auto_json

        # No side-info provided or file missing -> skip (proceed to EMBED in API)
        if not sideinfo_path or not os.path.exists(sideinfo_path):
            return {
                "status": "skip_no_sideinfo",
                "reason": "No .wm.json provided/found for this image. Proceed to embedding."
            }

        # Load side-info JSON written after embedding (with guards)
        try:
            with open(sideinfo_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            alpha        = float(meta["wm_params"]["alpha"])
            wavelet_name = meta["wm_params"]["wavelet"]
            canonical_wh = tuple(meta.get("canonical_size", [0, 0]))  # (W, H)
            S_R = np.array(meta["host_S"]["R"], dtype=np.float64)
            S_G = np.array(meta["host_S"]["G"], dtype=np.float64)
            S_B = np.array(meta["host_S"]["B"], dtype=np.float64)
            
            # Handle watermark logo - either from base64 or file path
            watermark_ref = meta["watermark_ref"]
            if "image_base64" in watermark_ref:
                # For backward compatibility, if base64 is provided in file-based sideinfo
                wm_logo_path = "base64_data"  # placeholder for later handling
            elif "path" in watermark_ref:
                wm_logo_path = watermark_ref["path"]
            else:
                return {"status": "skip_bad_meta", "reason": "Missing watermark reference (path or image_base64). Proceed to embedding."}
        except FileNotFoundError:
            return {"status": "skip_no_sideinfo", "reason": "Side-info file missing. Proceed to embedding."}
        except KeyError as e:
            return {"status": "skip_bad_meta", "reason": f"Missing key {e}. Proceed to embedding."}
        except Exception as e:
            return {"status": "skip_bad_meta", "reason": f"Unreadable side-info: {e}. Proceed to embedding."}

        # Load the images
        try:
            if wm_logo_path == "base64_data":
                # Load watermark from base64
                watermark_logo = self._decode_base64_to_pil(watermark_ref["image_base64"]).convert("RGB")
                wm_logo_source = "base64_data"
            else:
                # Validate watermark logo path
                if not os.path.exists(wm_logo_path):
                    return {"status": "skip_bad_meta", "reason": "Watermark logo path invalid. Proceed to embedding."}
                # Load watermark from file
                watermark_logo = Image.open(wm_logo_path).convert("RGB")
                wm_logo_source = wm_logo_path
                
            suspect_img = Image.open(suspect_path).convert("RGB")
        except Exception as e:
            return {"status": "skip_bad_meta", "reason": f"Image open failed: {e}. Proceed to embedding."}

        # Resize both to canonical size (from embed); fallback to suspect size if there is no canonical size
        if canonical_wh != (0, 0):
            watermark_logo = watermark_logo.resize(canonical_wh)
            suspect_img    = suspect_img.resize(canonical_wh)
        else:
            canonical_wh = suspect_img.size  

        # Split channels → float64
        wmr, wmg, wmb = [np.float64(c) for c in watermark_logo.split()]
        sur, sug, sub = [np.float64(c) for c in suspect_img.split()]

        # Extract each color channels
        ext_r = self._extract_channel(sur, wmr, S_R, wavelet_name, alpha, "Red")
        ext_g = self._extract_channel(sug, wmg, S_G, wavelet_name, alpha, "Green")
        ext_b = self._extract_channel(sub, wmb, S_B, wavelet_name, alpha, "Blue")

        # Save the extracted watermark image
        r8, g8, b8 = map(self._to_uint8, (ext_r, ext_g, ext_b))
        out_img = Image.merge("RGB", (Image.fromarray(r8), Image.fromarray(g8), Image.fromarray(b8)))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        out_img.save(out_path)

        return {
            "status": "ok_extracted",
            "alpha": alpha,
            "wavelet": wavelet_name,
            "canonical_size": canonical_wh,
            "sideinfo_used": sideinfo_path,
            "watermark_logo": wm_logo_source,
            "extracted_path": out_path
        }
    
    def _extract_from_suspect_with_meta(self, suspect_path: str, meta: Dict[str, Any], out_path: str, sideinfo_used: Optional[str]) -> Dict[str, Any]:
        """Same as _extract_from_suspect but uses an already-fetched meta dict (e.g., from DB/URL)."""
        try:
            alpha        = float(meta["wm_params"]["alpha"])
            wavelet_name = meta["wm_params"]["wavelet"]
            canonical_wh = tuple(meta.get("canonical_size", [0, 0]))  # (W, H)
            S_R = np.array(meta["host_S"]["R"], dtype=np.float64)
            S_G = np.array(meta["host_S"]["G"], dtype=np.float64)
            S_B = np.array(meta["host_S"]["B"], dtype=np.float64)
            
            # Handle watermark logo - either from base64 or file path
            watermark_ref = meta["watermark_ref"]
            if "image_base64" in watermark_ref:
                # Use base64 image data
                watermark_logo = self._decode_base64_to_pil(watermark_ref["image_base64"])
                wm_logo_source = "base64_data"
            elif "path" in watermark_ref:
                # Use file path (backward compatibility)
                wm_logo_path = watermark_ref["path"]
                if not os.path.exists(wm_logo_path):
                    return {"status": "skip_bad_meta", "reason": "Watermark logo path invalid. Proceed to embedding."}
                watermark_logo = Image.open(wm_logo_path).convert("RGB")
                wm_logo_source = wm_logo_path
            else:
                return {"status": "skip_bad_meta", "reason": "Missing watermark reference (path or image_base64). Proceed to embedding."}
                
        except KeyError as e:
            return {"status": "skip_bad_meta", "reason": f"Missing key {e}. Proceed to embedding."}
        except Exception as e:
            return {"status": "skip_bad_meta", "reason": f"Unreadable side-info: {e}. Proceed to embedding."}

        try:
            watermark_logo = watermark_logo.convert("RGB")
            suspect_img    = Image.open(suspect_path).convert("RGB")
        except Exception as e:
            return {"status": "skip_bad_meta", "reason": f"Image open failed: {e}. Proceed to embedding."}

        if canonical_wh != (0, 0):
            watermark_logo = watermark_logo.resize(canonical_wh)
            suspect_img    = suspect_img.resize(canonical_wh)
        else:
            canonical_wh = suspect_img.size

        wmr, wmg, wmb = [np.float64(c) for c in watermark_logo.split()]
        sur, sug, sub = [np.float64(c) for c in suspect_img.split()]

        ext_r = self._extract_channel(sur, wmr, S_R, wavelet_name, alpha, "Red")
        ext_g = self._extract_channel(sug, wmg, S_G, wavelet_name, alpha, "Green")
        ext_b = self._extract_channel(sub, wmb, S_B, wavelet_name, alpha, "Blue")

        r8, g8, b8 = map(self._to_uint8, (ext_r, ext_g, ext_b))
        out_img = Image.merge("RGB", (Image.fromarray(r8), Image.fromarray(g8), Image.fromarray(b8)))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        out_img.save(out_path)

        return {
            "status": "ok_extracted",
            "alpha": alpha,
            "wavelet": wavelet_name,
            "canonical_size": canonical_wh,
            "sideinfo_used": sideinfo_used,
            "watermark_logo": wm_logo_source,
            "extracted_path": out_path
        }
    
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
