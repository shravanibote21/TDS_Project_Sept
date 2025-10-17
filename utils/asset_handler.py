"""
Asset handler for extracting base64 data URIs from HTML and uploading them to GitHub.
Prevents LLM token limit issues and improves page load performance.
"""
import re
import base64
from typing import List, Tuple
from github import GithubException
from .logger import get_logger

logger = get_logger(__name__)


def extract_data_uris(html: str, size_threshold: int = 10000) -> List[Tuple[str, str, str]]:
    """
    Extract data URIs from HTML that exceed size threshold.
    
    Args:
        html: HTML content to scan
        size_threshold: Minimum size in bytes to extract (default 10KB)
    
    Returns:
        List of tuples: (full_data_uri, mime_type, base64_data)
    """
    pattern = r'data:([^;,]+);base64,([A-Za-z0-9+/=]+)'
    
    matches = []
    for match in re.finditer(pattern, html):
        full_uri = match.group(0)
        mime_type = match.group(1)
        base64_data = match.group(2)
        
        estimated_size = len(base64_data) * 3 // 4
        
        if estimated_size >= size_threshold:
            matches.append((full_uri, mime_type, base64_data))
            logger.info("Found large data URI: %s (~%s bytes)", mime_type, estimated_size)
    
    return matches


def mime_to_extension(mime_type: str) -> str:
    """Convert MIME type to file extension."""
    mime_map = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'image/gif': 'gif',
        'image/svg+xml': 'svg',
        'image/webp': 'webp',
        'image/bmp': 'bmp',
        'image/ico': 'ico',
        'image/icon': 'ico',
        'image/x-icon': 'ico',
        
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'video/ogg': 'ogv',
        'video/avi': 'avi',
        'video/mpeg': 'mpg',
        
        'audio/mpeg': 'mp3',
        'audio/mp3': 'mp3',
        'audio/ogg': 'ogg',
        'audio/wav': 'wav',
        'audio/webm': 'weba',
        'audio/aac': 'aac',
        
        'application/pdf': 'pdf',
        'text/plain': 'txt',
        'text/css': 'css',
        'text/javascript': 'js',
        'application/javascript': 'js',
    }
    
    mime_type = mime_type.lower().strip()
    
    if mime_type in mime_map:
        return mime_map[mime_type]
    
    if '/' in mime_type:
        subtype = mime_type.split('/')[-1]
        subtype = subtype.split(';')[0].strip()
        return subtype
    
    return 'bin'


def upload_asset_to_repo(repo, filename: str, content: bytes, message: str = None) -> str:
    """
    Upload a file to GitHub repository root.
    
    Args:
        repo: PyGithub repository object
        filename: Name of file to create
        content: Binary content to upload
        message: Commit message
    
    Returns:
        Relative path to the file
    """
    message = message or f"Add asset: {filename}"
    
    try:
        try:
            existing_file = repo.get_contents(filename, ref="main")
            repo.update_file(
                path=filename,
                message=message,
                content=content,
                sha=existing_file.sha,
                branch="main"
            )
            logger.info("Updated existing asset: %s", filename)
        except GithubException as e:
            if e.status == 404:
                repo.create_file(
                    path=filename,
                    message=message,
                    content=content,
                    branch="main"
                )
                logger.info("Created new asset: %s", filename)
            else:
                raise
        
        return filename
    except Exception as e:
        logger.warning("Error uploading asset %s: %s", filename, str(e))
        raise


def process_html_assets(html: str, repo, round_num: int = 1) -> str:
    """
    Extract large data URIs from HTML, upload them to GitHub, and replace with relative paths.
    
    Args:
        html: Original HTML content with data URIs
        repo: PyGithub repository object
        round_num: Round number for file naming
    
    Returns:
        Modified HTML with data URIs replaced by relative paths
    """
    data_uris = extract_data_uris(html, size_threshold=10000)
    
    if not data_uris:
        logger.info("No large data URIs found in HTML")
        return html
    
    logger.info("Processing %s large data URI(s)...", len(data_uris))
    
    asset_counter = {}
    
    for full_uri, mime_type, base64_data in data_uris:
        try:
            content = base64.b64decode(base64_data)
            
            extension = mime_to_extension(mime_type)
            
            if extension not in asset_counter:
                asset_counter[extension] = 0
            asset_counter[extension] += 1
            
            if asset_counter[extension] == 1:
                filename = f"asset_round{round_num}_{extension.replace('.', '')}.{extension}"
            else:
                filename = f"asset_round{round_num}_{extension.replace('.', '')}{asset_counter[extension]}.{extension}"
            
            upload_asset_to_repo(
                repo=repo,
                filename=filename,
                content=content,
                message=f"Add {extension.upper()} asset for round {round_num}"
            )
            
            html = html.replace(full_uri, filename)
            logger.info("Replaced data URI with: %s", filename)
            
        except Exception as e:
            logger.warning("Failed to process asset %s: %s", mime_type, str(e))
            continue
    
    return html


def test_asset_handler():
    """Test the asset extraction logic."""
    test_html = '''
    <html>
    <body>
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" alt="small">
        <img src="data:image/png;base64,''' + 'A' * 15000 + '''=" alt="large">
        <video><source src="data:video/mp4;base64,''' + 'B' * 20000 + '''"></video>
    </body>
    </html>
    '''
    
    uris = extract_data_uris(test_html, size_threshold=10000)
    print(f"\nFound {len(uris)} large data URIs:")
    for uri, mime, data in uris:
        print(f"  - {mime}: {len(data)} chars (~{len(data) * 3 // 4} bytes)")


if __name__ == "__main__":
    test_asset_handler()
