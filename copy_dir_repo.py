#!/usr/bin/env python3
"""
Script to copy folders and files from one repository to another using GitHub raw URLs
Supports copying entire directories recursively
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class GitHubFolderCopier:
    def __init__(self, source_repo: str, branch: str = "main", max_workers: int = 5):
        """
        Initialize the copier with source repository and branch
        
        Args:
            source_repo: GitHub repository in format "username/repo" or full URL
            branch: Branch name (default: main)
            max_workers: Number of parallel downloads (default: 5)
        """
        self.source_repo = self._parse_repo_url(source_repo)
        self.branch = branch
        self.max_workers = max_workers
        self.base_api_url = f"https://api.github.com/repos/{self.source_repo}/contents"
        self.base_raw_url = f"https://raw.githubusercontent.com/{self.source_repo}/{self.branch}"
        
    def _parse_repo_url(self, repo: str) -> str:
        """Parse repository URL to username/repo format"""
        repo = repo.replace("https://github.com/", "")
        repo = repo.replace("git@github.com:", "")
        repo = repo.replace(".git", "")
        return repo.strip("/")
    
    def _get_github_contents(self, path: str) -> Optional[List[Dict]]:
        """
        Get contents of a directory from GitHub API
        
        Args:
            path: Path in the repository
            
        Returns:
            List of file/directory info or None if error
        """
        url = f"{self.base_api_url}/{path}?ref={self.branch}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/vnd.github.v3+json'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                return data
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"⚠️  Path not found: {path}")
            else:
                print(f"❌ HTTP Error {e.code}: {url}")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def _download_file(self, source_path: str, dest_path: str, force: bool = False) -> bool:
        """
        Download a single file from source repository
        
        Args:
            source_path: Path to file in source repository
            dest_path: Destination path in local filesystem
            force: Overwrite existing file if True
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_raw_url}/{source_path}"
        dest = Path(dest_path)
        
        if dest.exists() and not force:
            print(f"⚠️  File exists: {dest_path} (use --force to overwrite)")
            return False
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Python Script)'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
            
            with open(dest, 'wb') as f:
                f.write(content)
            
            print(f"  ✓ {dest_path}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed: {source_path} - {str(e)}")
            return False
    
    def _get_all_files_in_folder(self, folder_path: str, max_depth: int = 10) -> List[str]:
        """
        Recursively get all file paths in a GitHub folder
        
        Args:
            folder_path: Path to folder in repository
            max_depth: Maximum recursion depth
            
        Returns:
            List of file paths relative to repository root
        """
        files = []
        
        def _recurse(current_path: str, depth: int):
            if depth > max_depth:
                return
            
            contents = self._get_github_contents(current_path)
            if not contents:
                return
            
            for item in contents:
                if item['type'] == 'file':
                    files.append(item['path'])
                elif item['type'] == 'dir':
                    _recurse(item['path'], depth + 1)
        
        _recurse(folder_path, 0)
        return files
    
    def copy_folder(self, source_folder: str, dest_folder: str, force: bool = False, 
                    recursive: bool = True, show_progress: bool = True) -> Tuple[int, int]:
        """
        Copy an entire folder recursively
        
        Args:
            source_folder: Source folder path in GitHub repo
            dest_folder: Destination path in local filesystem
            force: Overwrite existing files
            recursive: Copy subdirectories recursively
            show_progress: Show progress bar
            
        Returns:
            Tuple of (success_count, total_count)
        """
        print(f"\n📁 Copying folder: {source_folder} -> {dest_folder}")
        
        # Get all files in the folder
        print(f"🔍 Scanning folder contents...")
        files = self._get_all_files_in_folder(source_folder) if recursive else []
        
        # If not recursive, try to get direct files only
        if not recursive:
            contents = self._get_github_contents(source_folder)
            if contents:
                files = [item['path'] for item in contents if item['type'] == 'file']
        
        if not files:
            print(f"⚠️  No files found in: {source_folder}")
            return 0, 0
        
        total = len(files)
        print(f"📦 Found {total} file(s) to copy")
        
        # Prepare destination paths
        downloads = []
        for src_file in files:
            # Calculate relative path
            rel_path = os.path.relpath(src_file, source_folder)
            dest_file = os.path.join(dest_folder, rel_path)
            downloads.append((src_file, dest_file))
        
        # Download files
        success_count = 0
        
        if show_progress:
            print(f"\n⬇️  Downloading {total} files...")
        
        for src_file, dest_file in downloads:
            if self._download_file(src_file, dest_file, force):
                success_count += 1
        
        print(f"\n✅ Copied {success_count}/{total} files from {source_folder}")
        return success_count, total
    
    def copy_folders(self, folders_config: List[Dict], force: bool = False) -> Tuple[int, int]:
        """
        Copy multiple folders from configuration
        
        Args:
            folders_config: List of dicts with 'source' and 'dest' keys
            force: Overwrite existing files
            
        Returns:
            Tuple of (success_count, total_count)
        """
        total_success = 0
        total_files = 0
        
        print(f"\n{'='*60}")
        print(f"📂 Copying {len(folders_config)} folder(s) from {self.source_repo}/{self.branch}")
        print(f"{'='*60}")
        
        for config in folders_config:
            source = config.get('source')
            dest = config.get('dest')
            recursive = config.get('recursive', True)
            
            if not source or not dest:
                print(f"⚠️  Invalid config: {config}")
                continue
            
            success, total = self.copy_folder(source, dest, force, recursive)
            total_success += success
            total_files += total
        
        print(f"\n{'='*60}")
        print(f"🎉 Total: {total_success}/{total_files} files copied successfully")
        print(f"{'='*60}")
        
        return total_success, total_files
    
    def copy_mixed(self, items_config: List[Dict], force: bool = False) -> Tuple[int, int]:
        """
        Copy mixed items (files and folders)
        
        Args:
            items_config: List of dicts with 'type', 'source', 'dest' keys
            force: Overwrite existing files
            
        Returns:
            Tuple of (success_count, total_count)
        """
        total_success = 0
        total_items = 0
        
        print(f"\n{'='*60}")
        print(f"📦 Copying {len(items_config)} item(s) from {self.source_repo}/{self.branch}")
        print(f"{'='*60}")
        
        for config in items_config:
            item_type = config.get('type', 'file')
            source = config.get('source')
            dest = config.get('dest')
            
            if not source or not dest:
                print(f"⚠️  Invalid config: {config}")
                continue
            
            if item_type == 'folder':
                recursive = config.get('recursive', True)
                success, total = self.copy_folder(source, dest, force, recursive)
                total_success += success
                total_items += total
            else:
                if self._download_file(source, dest, force):
                    total_success += 1
                total_items += 1
        
        print(f"\n{'='*60}")
        print(f"🎉 Total: {total_success}/{total_items} items copied successfully")
        print(f"{'='*60}")
        
        return total_success, total_items
    
    def copy_from_json(self, json_file: str, force: bool = False) -> Tuple[int, int]:
        """
        Copy files/folders using JSON configuration file
        
        Args:
            json_file: Path to JSON configuration file
            force: Overwrite existing files
            
        Returns:
            Tuple of (success_count, total_count)
        """
        try:
            with open(json_file, 'r') as f:
                config_data = json.load(f)
            
            if isinstance(config_data, dict):
                if 'source_repo' in config_data:
                    self.source_repo = self._parse_repo_url(config_data['source_repo'])
                    self.base_api_url = f"https://api.github.com/repos/{self.source_repo}/contents"
                    self.base_raw_url = f"https://raw.githubusercontent.com/{self.source_repo}/{self.branch}"
                
                if 'branch' in config_data:
                    self.branch = config_data['branch']
                    self.base_raw_url = f"https://raw.githubusercontent.com/{self.source_repo}/{self.branch}"
                
                # Handle different config formats
                if 'folders' in config_data:
                    return self.copy_folders(config_data['folders'], force)
                elif 'files' in config_data:
                    return self._copy_files_from_config(config_data['files'], force)
                elif 'items' in config_data:
                    return self.copy_mixed(config_data['items'], force)
                else:
                    print(f"❌ Invalid config format. Use 'folders', 'files', or 'items' key")
                    return 0, 0
            else:
                print(f"❌ Config must be a JSON object")
                return 0, 0
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON file: {e}")
            return 0, 0
        except FileNotFoundError:
            print(f"❌ File not found: {json_file}")
            return 0, 0
    
    def _copy_files_from_config(self, files_config: List[Dict], force: bool = False) -> Tuple[int, int]:
        """Internal method to copy files from config"""
        success_count = 0
        total_count = len(files_config)
        
        for config in files_config:
            source = config.get('source')
            dest = config.get('dest')
            if source and dest:
                if self._download_file(source, dest, force):
                    success_count += 1
        
        return success_count, total_count


def main():
    parser = argparse.ArgumentParser(
        description='Copy folders and files from GitHub repository using raw URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Copy single file
  python copy_github_folder.py -s Samo1408/Builder_kernel -b m32-new -t file -f fs/exec.c -d kernel_root/fs/exec.c
  
  # Copy entire folder
  python copy_github_folder.py -s Samo1408/Builder_kernel -b m32-new -t folder -f fs -d kernel_root/fs
  
  # Copy using JSON config
  python copy_github_folder.py -c config.json --force

JSON Config Format:
  {
    "source_repo": "Samo1408/Builder_kernel",
    "branch": "m32-new",
    "folders": [
      {"source": "fs", "dest": "kernel_root/fs", "recursive": true},
      {"source": "kernel", "dest": "kernel_root/kernel", "recursive": true}
    ]
  }
  
  Or mixed items:
  {
    "source_repo": "Samo1408/Builder_kernel",
    "branch": "m32-new",
    "items": [
      {"type": "file", "source": "build.sh", "dest": "build.sh"},
      {"type": "folder", "source": "fs", "dest": "kernel_root/fs", "recursive": true}
    ]
  }
        """
    )
    
    parser.add_argument('-s', '--source', help='Source repository (username/repo or full URL)')
    parser.add_argument('-b', '--branch', default='main', help='Branch name (default: main)')
    parser.add_argument('-t', '--type', choices=['file', 'folder'], help='Type: file or folder')
    parser.add_argument('-f', '--file', help='Source path (file path or folder path)')
    parser.add_argument('-d', '--dest', help='Destination path')
    parser.add_argument('-c', '--config', help='JSON configuration file')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be copied without actual download')
    parser.add_argument('--no-recursive', action='store_true', help='Don\'t copy subdirectories (folders only)')
    parser.add_argument('--workers', type=int, default=5, help='Parallel downloads (default: 5)')
    
    args = parser.parse_args()
    
    # Handle single item copy
    if args.file and args.dest and args.type:
        copier = GitHubFolderCopier(args.source, args.branch, args.workers)
        
        if args.dry_run:
            print(f"[DRY RUN] Would copy {args.type}: {args.file} -> {args.dest}")
            return 0
        
        if args.type == 'file':
            success = copier._download_file(args.file, args.dest, args.force)
            return 0 if success else 1
        else:  # folder
            success, total = copier.copy_folder(args.file, args.dest, args.force, not args.no_recursive)
            return 0 if success == total else 1
    
    # Handle config file copy
    elif args.config:
        if args.dry_run:
            print(f"[DRY RUN] Would copy items from config: {args.config}")
            try:
                with open(args.config, 'r') as f:
                    config = json.load(f)
                print(json.dumps(config, indent=2))
            except:
                pass
            return 0
        
        copier = GitHubFolderCopier(args.source if args.source else "", args.branch, args.workers)
        success, total = copier.copy_from_json(args.config, args.force)
        return 0 if success == total else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())