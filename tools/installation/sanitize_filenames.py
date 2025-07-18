#!/usr/bin/env python3
"""
Sanitize Filenames for VLC Compatibility
Removes spaces and special characters from filenames in downloads directory
"""

import os
import re
import shutil
from pathlib import Path
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing problematic characters"""
    # Remove or replace problematic characters
    sanitized = filename
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove or replace special characters
    sanitized = re.sub(r'[!@#$%^&*()\[\]{}|\\:;"\'<>?,./]', '', sanitized)
    
    # Replace multiple underscores with single underscore
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized

def sanitize_downloads_directory(downloads_dir: str = "downloads", dry_run: bool = False) -> dict:
    """Sanitize all filenames in the downloads directory"""
    downloads_path = Path(downloads_dir)
    
    if not downloads_path.exists():
        logger.error(f"Downloads directory not found: {downloads_path}")
        return {"error": "Directory not found"}
    
    # Get all files in the directory
    all_files = list(downloads_path.glob("*"))
    
    # Group files by their base name (before extensions)
    file_groups = {}
    for file_path in all_files:
        if file_path.is_file():
            # Extract base name and extension
            base_name = file_path.stem
            extension = file_path.suffix
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append((file_path, extension))
    
    # Sanitize each group
    changes = {
        "renamed_files": [],
        "errors": [],
        "total_files": len(all_files)
    }
    
    for base_name, files in file_groups.items():
        sanitized_base = sanitize_filename(base_name)
        
        if sanitized_base != base_name:
            logger.info(f"Sanitizing: '{base_name}' -> '{sanitized_base}'")
            
            # Rename all files with this base name
            for file_path, extension in files:
                old_path = file_path
                new_path = file_path.parent / f"{sanitized_base}{extension}"
                
                try:
                    if not dry_run:
                        # Check if target file already exists
                        if new_path.exists():
                            logger.warning(f"Target file already exists: {new_path}")
                            # Add timestamp to avoid conflicts
                            timestamp = int(time.time())
                            new_path = file_path.parent / f"{sanitized_base}_{timestamp}{extension}"
                        
                        shutil.move(str(old_path), str(new_path))
                        logger.info(f"  Renamed: {old_path.name} -> {new_path.name}")
                        changes["renamed_files"].append({
                            "old": str(old_path),
                            "new": str(new_path)
                        })
                    else:
                        logger.info(f"  Would rename: {old_path.name} -> {new_path.name}")
                        changes["renamed_files"].append({
                            "old": str(old_path),
                            "new": str(new_path)
                        })
                        
                except Exception as e:
                    error_msg = f"Failed to rename {old_path}: {e}"
                    logger.error(error_msg)
                    changes["errors"].append(error_msg)
        else:
            logger.debug(f"No changes needed for: {base_name}")
    
    return changes

def main():
    parser = argparse.ArgumentParser(description="Sanitize filenames in downloads directory")
    parser.add_argument("--directory", default="downloads", help="Directory to sanitize")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    
    args = parser.parse_args()
    
    print(f"🔧 Sanitizing filenames in: {args.directory}")
    if args.dry_run:
        print("📋 DRY RUN MODE - No files will be changed")
    
    # Import time for timestamp generation
    import time
    
    changes = sanitize_downloads_directory(args.directory, args.dry_run)
    
    if "error" in changes:
        print(f"❌ Error: {changes['error']}")
        return
    
    print(f"\n📊 Sanitization Results:")
    print(f"   Total files found: {changes['total_files']}")
    print(f"   Files renamed: {len(changes['renamed_files'])}")
    print(f"   Errors: {len(changes['errors'])}")
    
    if changes["renamed_files"]:
        print(f"\n✅ Renamed files:")
        for change in changes["renamed_files"]:
            old_name = Path(change["old"]).name
            new_name = Path(change["new"]).name
            print(f"   {old_name} -> {new_name}")
    
    if changes["errors"]:
        print(f"\n❌ Errors:")
        for error in changes["errors"]:
            print(f"   {error}")
    
    if not args.dry_run and changes["renamed_files"]:
        print(f"\n🎉 Filenames sanitized successfully!")
        print(f"   All files are now VLC-compatible")
    elif args.dry_run:
        print(f"\n📋 Dry run completed - use without --dry-run to apply changes")

if __name__ == "__main__":
    main() 