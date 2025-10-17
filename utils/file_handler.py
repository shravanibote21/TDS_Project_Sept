import base64
import mimetypes
from typing import Dict, Optional, Any
import json


MAX_FULL_CONTENT_CHARS = 20000
MAX_PREVIEW_LINES = 10


def decode_base64_content(content: str) -> bytes:
    try:
        if "," in content:
            base64_data = content.split(",", 1)[1]
        else:
            base64_data = content
        
        padding = 4 - (len(base64_data) % 4)
        if padding != 4:
            base64_data += "=" * padding
        
        return base64.b64decode(base64_data)
    except Exception:
        try:
            return base64.b64decode(content)
        except Exception:
            return b""


def decode_to_text(data: bytes, encodings: list = None) -> str:
    if encodings is None:
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1", "ascii"]
    
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except Exception:
            continue
    
    return data.decode("utf-8", errors="ignore")


def extract_mime_type(data_uri: str) -> str:
    if not data_uri.startswith("data:"):
        return "application/octet-stream"
    
    try:
        mime_part = data_uri.split(";")[0].replace("data:", "")
        return mime_part if mime_part else "application/octet-stream"
    except Exception:
        return "application/octet-stream"


def is_text_file(filename: str, mime_type: str = None) -> bool:
    text_extensions = {
        ".txt", ".md", ".markdown", ".csv", ".tsv", ".log", ".json", ".xml",
        ".yaml", ".yml", ".ini", ".conf", ".config", ".env", ".properties",
        ".sh", ".bash", ".bat", ".ps1", ".py", ".js", ".ts", ".jsx", ".tsx",
        ".html", ".htm", ".css", ".scss", ".sass", ".less", ".sql", ".r",
        ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".go",
        ".rs", ".swift", ".kt", ".scala", ".pl", ".lua", ".vim", ".gitignore",
        ".dockerfile", ".makefile", ".cmake", ".gradle", ".maven", ".toml"
    }
    
    lower_name = filename.lower()
    
    for ext in text_extensions:
        if lower_name.endswith(ext):
            return True
    
    if mime_type:
        if mime_type.startswith("text/"):
            return True
        if "json" in mime_type or "xml" in mime_type or "yaml" in mime_type:
            return True
    
    return False


def is_image_file(filename: str) -> bool:
    image_extensions = {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg",
        ".ico", ".tiff", ".tif", ".avif", ".apng"
    }
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def is_video_file(filename: str) -> bool:
    video_extensions = {
        ".mp4", ".webm", ".ogg", ".ogv", ".mov", ".avi", ".mkv",
        ".flv", ".wmv", ".m4v", ".3gp"
    }
    return any(filename.lower().endswith(ext) for ext in video_extensions)


def is_audio_file(filename: str) -> bool:
    audio_extensions = {
        ".mp3", ".wav", ".ogg", ".oga", ".m4a", ".flac", ".aac",
        ".wma", ".opus", ".webm"
    }
    return any(filename.lower().endswith(ext) for ext in audio_extensions)


def is_document_file(filename: str) -> bool:
    document_extensions = {
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".odt", ".ods", ".odp", ".rtf", ".pages", ".numbers", ".key"
    }
    return any(filename.lower().endswith(ext) for ext in document_extensions)


def process_text_content(data: bytes, filename: str) -> Dict[str, Any]:
    text_content = decode_to_text(data)
    lines = text_content.splitlines()
    total_lines = len(lines)
    content_length = len(text_content)
    
    send_full_content = content_length <= MAX_FULL_CONTENT_CHARS
    
    preview_lines = min(MAX_PREVIEW_LINES, total_lines)
    preview = []
    
    if not send_full_content:
        for i in range(preview_lines):
            line = lines[i]
            if len(line) > 300:
                line = line[:300] + "..."
            preview.append(line)
    
    return {
        "type": "text",
        "filename": filename,
        "total_lines": total_lines,
        "preview_lines": preview_lines if not send_full_content else total_lines,
        "preview": preview,
        "full_content": text_content,
        "send_full": send_full_content,
        "encoding_used": "utf-8",
        "size_bytes": len(data),
        "char_count": content_length
    }


def process_markdown_content(data: bytes, filename: str) -> Dict[str, Any]:
    text_info = process_text_content(data, filename)
    text_info["type"] = "markdown"
    text_info["needs_conversion"] = True
    text_info["conversion_target"] = "HTML"
    return text_info


def process_csv_content(data: bytes, filename: str) -> Dict[str, Any]:
    text_content = decode_to_text(data)
    lines = text_content.splitlines()
    content_length = len(text_content)
    
    send_full_content = content_length <= MAX_FULL_CONTENT_CHARS
    
    rows = []
    max_preview_rows = 20 if not send_full_content else len(lines)
    
    for i, line in enumerate(lines[:max_preview_rows]):
        if line.strip():
            cells = line.split(",")
            rows.append(cells)
    
    return {
        "type": "csv",
        "filename": filename,
        "total_lines": len(lines),
        "preview_rows": len(rows),
        "rows": rows,
        "full_content": text_content,
        "send_full": send_full_content,
        "size_bytes": len(data),
        "char_count": content_length
    }


def process_json_content(data: bytes, filename: str) -> Dict[str, Any]:
    text_content = decode_to_text(data)
    content_length = len(text_content)
    
    send_full_content = content_length <= MAX_FULL_CONTENT_CHARS
    
    try:
        json_data = json.loads(text_content)
        formatted = json.dumps(json_data, indent=2)
        if send_full_content:
            preview_lines = formatted.splitlines()
        else:
            preview_lines = formatted.splitlines()[:20]
    except Exception:
        if send_full_content:
            preview_lines = text_content.splitlines()
        else:
            preview_lines = text_content.splitlines()[:20]
    
    return {
        "type": "json",
        "filename": filename,
        "preview": preview_lines,
        "full_content": text_content,
        "send_full": send_full_content,
        "size_bytes": len(data),
        "char_count": content_length
    }


def process_image_content(url: str, filename: str) -> Dict[str, Any]:
    mime_type = extract_mime_type(url) if url.startswith("data:") else mimetypes.guess_type(filename)[0]
    
    size_estimate = 0
    if url.startswith("data:"):
        if "base64" in url:
            try:
                base64_data = url.split(",", 1)[1]
                size_estimate = len(base64.b64decode(base64_data))
            except Exception:
                pass
    
    return {
        "type": "image",
        "filename": filename,
        "mime_type": mime_type or "image/unknown",
        "url": url,
        "is_data_uri": url.startswith("data:"),
        "is_remote": url.startswith(("http://", "https://")),
        "size_bytes": size_estimate,
        "embed_tag": f'<img src="{url if not url.startswith("data:") else "{{DATA_URI}}"}" alt="{filename}">'
    }


def process_video_content(url: str, filename: str) -> Dict[str, Any]:
    mime_type = extract_mime_type(url) if url.startswith("data:") else mimetypes.guess_type(filename)[0]
    
    return {
        "type": "video",
        "filename": filename,
        "mime_type": mime_type or "video/unknown",
        "url": url,
        "is_data_uri": url.startswith("data:"),
        "is_remote": url.startswith(("http://", "https://")),
        "embed_tag": f'<video src="{url if not url.startswith("data:") else "{{DATA_URI}}"}" controls></video>'
    }


def process_audio_content(url: str, filename: str) -> Dict[str, Any]:
    mime_type = extract_mime_type(url) if url.startswith("data:") else mimetypes.guess_type(filename)[0]
    
    return {
        "type": "audio",
        "filename": filename,
        "mime_type": mime_type or "audio/unknown",
        "url": url,
        "is_data_uri": url.startswith("data:"),
        "is_remote": url.startswith(("http://", "https://")),
        "embed_tag": f'<audio src="{url if not url.startswith("data:") else "{{DATA_URI}}"}" controls></audio>'
    }


def process_document_content(url: str, filename: str) -> Dict[str, Any]:
    mime_type = extract_mime_type(url) if url.startswith("data:") else mimetypes.guess_type(filename)[0]
    
    needs_conversion = filename.lower().endswith((".md", ".docx", ".doc", ".rtf", ".odt"))
    conversion_target = "HTML" if needs_conversion else None
    
    return {
        "type": "document",
        "filename": filename,
        "mime_type": mime_type or "application/octet-stream",
        "url": url,
        "is_data_uri": url.startswith("data:"),
        "is_remote": url.startswith(("http://", "https://")),
        "needs_conversion": needs_conversion,
        "conversion_target": conversion_target,
        "download_tag": f'<a href="{url if not url.startswith("data:") else "{{DATA_URI}}"}" download="{filename}">Download {filename}</a>'
    }


def process_attachment(attachment: Any) -> Dict[str, Any]:
    if isinstance(attachment, str):
        if attachment.startswith("data:"):
            mime_type = extract_mime_type(attachment)
            filename = "attachment"
            
            if "image" in mime_type:
                return process_image_content(attachment, "image")
            elif "video" in mime_type:
                return process_video_content(attachment, "video")
            elif "audio" in mime_type:
                return process_audio_content(attachment, "audio")
            else:
                decoded = decode_base64_content(attachment)
                return process_text_content(decoded, filename)
        
        elif attachment.startswith(("http://", "https://")):
            return {
                "type": "remote_url",
                "url": attachment,
                "filename": attachment.split("/")[-1] if "/" in attachment else "resource"
            }
        
        else:
            return {
                "type": "string_data",
                "content": attachment[:1000],
                "full_length": len(attachment)
            }
    
    if not isinstance(attachment, dict):
        return {"type": "unknown", "data": str(attachment)[:500]}
    
    name = attachment.get("name", attachment.get("filename", "unknown"))
    url = attachment.get("url", attachment.get("data", attachment.get("content", "")))
    
    if not url and "path" in attachment:
        try:
            with open(attachment["path"], "rb") as f:
                file_data = f.read()
            
            if is_text_file(name):
                return process_text_content(file_data, name)
            else:
                encoded = base64.b64encode(file_data).decode("ascii")
                mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
                url = f"data:{mime};base64,{encoded}"
        except Exception:
            return {"type": "error", "filename": name, "error": "Could not read file"}
    
    if not url:
        return {"type": "empty", "filename": name}
    
    if isinstance(url, bytes):
        if is_text_file(name):
            return process_text_content(url, name)
        else:
            encoded = base64.b64encode(url).decode("ascii")
            mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
            url = f"data:{mime};base64,{encoded}"
    
    if url.startswith("data:"):
        decoded_data = decode_base64_content(url)
        
        if is_text_file(name):
            if name.lower().endswith(".md"):
                return process_markdown_content(decoded_data, name)
            elif name.lower().endswith((".csv", ".tsv")):
                return process_csv_content(decoded_data, name)
            elif name.lower().endswith(".json"):
                return process_json_content(decoded_data, name)
            else:
                return process_text_content(decoded_data, name)
        
        elif is_image_file(name):
            return process_image_content(url, name)
        
        elif is_video_file(name):
            return process_video_content(url, name)
        
        elif is_audio_file(name):
            return process_audio_content(url, name)
        
        elif is_document_file(name):
            return process_document_content(url, name)
        
        else:
            try:
                text_attempt = decode_to_text(decoded_data)
                if len(text_attempt) > 0 and text_attempt.isprintable() or "\n" in text_attempt:
                    return process_text_content(decoded_data, name)
            except Exception:
                pass
            
            return {
                "type": "binary",
                "filename": name,
                "size_bytes": len(decoded_data),
                "data_uri": url
            }
    
    elif url.startswith(("http://", "https://")):
        if is_image_file(name):
            return process_image_content(url, name)
        elif is_video_file(name):
            return process_video_content(url, name)
        elif is_audio_file(name):
            return process_audio_content(url, name)
        elif is_document_file(name):
            return process_document_content(url, name)
        else:
            return {
                "type": "remote_file",
                "filename": name,
                "url": url
            }
    
    else:
        if len(url) > 1000:
            try:
                decoded_data = decode_base64_content(url)
                if is_text_file(name):
                    return process_text_content(decoded_data, name)
                else:
                    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
                    data_uri = f"data:{mime};base64,{url}"
                    
                    if is_image_file(name):
                        return process_image_content(data_uri, name)
                    elif is_video_file(name):
                        return process_video_content(data_uri, name)
                    elif is_audio_file(name):
                        return process_audio_content(data_uri, name)
                    
                    return {
                        "type": "binary",
                        "filename": name,
                        "data_uri": data_uri
                    }
            except Exception:
                pass
        
        return {
            "type": "string_reference",
            "filename": name,
            "reference": url[:200]
        }


def format_attachment_info(processed: Dict[str, Any]) -> str:
    info_type = processed.get("type", "unknown")
    filename = processed.get("filename", "unknown")
    
    result = f"\n--- {filename} ---\n"
    result += f"Type: {info_type}\n"
    
    if info_type == "text":
        result += f"Lines: {processed.get('total_lines', 0)}\n"
        result += f"Characters: {processed.get('char_count', 0)}\n"
        result += f"Size: {processed.get('size_bytes', 0)} bytes\n"
        
        if processed.get('send_full'):
            result += "\n=== FULL CONTENT ===\n"
            result += processed.get('full_content', '')
            result += "\n=== END CONTENT ===\n"
        else:
            result += f"\nPreview (first {processed.get('preview_lines', 0)} lines):\n"
            for i, line in enumerate(processed.get('preview', []), 1):
                result += f"{i}. {line}\n"
    
    elif info_type == "markdown":
        result += f"Lines: {processed.get('total_lines', 0)}\n"
        result += f"Characters: {processed.get('char_count', 0)}\n"
        result += f"Conversion needed: YES ({processed.get('conversion_target', 'HTML')})\n"
        
        if processed.get('send_full'):
            result += "\n=== FULL MARKDOWN CONTENT ===\n"
            result += processed.get('full_content', '')
            result += "\n=== END MARKDOWN ===\n"
        else:
            result += f"\nPreview (first {processed.get('preview_lines', 0)} lines):\n"
            for i, line in enumerate(processed.get('preview', []), 1):
                result += f"{i}. {line}\n"
    
    elif info_type == "csv":
        result += f"Total rows: {processed.get('total_lines', 0)}\n"
        result += f"Characters: {processed.get('char_count', 0)}\n"
        
        if processed.get('send_full'):
            result += "\n=== FULL CSV CONTENT ===\n"
            result += processed.get('full_content', '')
            result += "\n=== END CSV ===\n"
        else:
            result += f"\nPreview (first {processed.get('preview_rows', 0)} rows):\n"
            for i, row in enumerate(processed.get('rows', [])[:10], 1):
                result += f"{i}. {', '.join(str(cell) for cell in row)}\n"
    
    elif info_type == "json":
        result += f"Characters: {processed.get('char_count', 0)}\n"
        result += f"Size: {processed.get('size_bytes', 0)} bytes\n"
        
        if processed.get('send_full'):
            result += "\n=== FULL JSON CONTENT ===\n"
            for line in processed.get('preview', []):
                result += f"{line}\n"
            result += "=== END JSON ===\n"
        else:
            result += "\nPreview (first 20 lines):\n"
            for line in processed.get('preview', []):
                result += f"{line}\n"
    
    elif info_type == "image":
        result += f"MIME: {processed.get('mime_type', 'unknown')}\n"
        if processed.get('size_bytes'):
            result += f"Size: ~{processed['size_bytes'] / 1024:.1f} KB\n"
        result += f"Data URI: {'YES' if processed.get('is_data_uri') else 'NO'}\n"
        result += f"Usage: {processed.get('embed_tag', '')}\n"
    
    elif info_type == "video":
        result += f"MIME: {processed.get('mime_type', 'unknown')}\n"
        result += f"Usage: {processed.get('embed_tag', '')}\n"
    
    elif info_type == "audio":
        result += f"MIME: {processed.get('mime_type', 'unknown')}\n"
        result += f"Usage: {processed.get('embed_tag', '')}\n"
    
    elif info_type == "document":
        result += f"MIME: {processed.get('mime_type', 'unknown')}\n"
        if processed.get('needs_conversion'):
            result += f"Conversion needed: YES ({processed.get('conversion_target', 'HTML')})\n"
        result += f"Usage: {processed.get('download_tag', '')}\n"
    
    elif info_type == "remote_file" or info_type == "remote_url":
        result += f"URL: {processed.get('url', '')}\n"
    
    elif info_type == "binary":
        result += f"Size: {processed.get('size_bytes', 0)} bytes\n"
        result += "Format: Binary data (base64 encoded in data URI)\n"
    
    result += "\n"
    return result


def process_all_attachments(attachments: Optional[list]) -> str:
    if not attachments:
        return ""
    
    result = "\n\n=== ATTACHMENTS ===\n"
    
    for i, att in enumerate(attachments, 1):
        try:
            processed = process_attachment(att)
            result += format_attachment_info(processed)
        except Exception as e:
            result += f"\n--- Attachment {i} ---\n"
            result += f"Error processing: {str(e)[:200]}\n\n"
    
    return result
