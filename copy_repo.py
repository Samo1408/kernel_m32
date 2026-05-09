#!/usr/bin/env python3
"""
Script to copy files from one repository to another using GitHub raw URLs
Supports copying multiple files with custom destination paths
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple
import shutil

class FileCopier:
    def __init__(self, source_repo: str, branch: str = "main"):
        """
        Initialize the copier with source repository and branch
        
        Args:
            source_repo: GitHub repository in format "username/repo" or full URL
            branch: Branch name (default: main)
        """
        self.source_repo = self._parse_repo_url(source_repo)
        self.branch = branch
        self.base_raw_url = f"https://raw.githubusercontent.com/{self.source_repo}/{self.branch}"
        
    def _parse_repo_url(self, repo: str) -> str:
        """Parse repository URL to username/repo format"""
        # Remove https://github.com/ if present
        repo = repo.replace("https://github.com/", "")
        repo = repo.replace("git@github.com:", "")
        repo = repo.replace(".git", "")
        return repo.strip("/")
    
    def download_file(self, source_path: str, dest_path: str, force: bool = False) -> bool:
        """
        Download a file from source repository to destination path
        
        Args:
            source_path: Path to file in source repository
            dest_path: Destination path in local filesystem
            force: Overwrite existing file if True
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_raw_url}/{source_path}"
        dest = Path(dest_path)
        
        # Check if destination exists
        if dest.exists() and not force:
            print(f"⚠️  File exists: {dest_path} (use --force to overwrite)")
            return False
        
        # Create destination directory if needed
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"📥 Downloading: {url}")
            print(f"   → Saving to: {dest_path}")
            
            # Download with timeout and proper headers
            headers = {'User-Agent': 'Mozilla/5.0 (Python Script)'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                
            # Write to file
            with open(dest, 'wb') as f:
                f.write(content)
                
            print(f"✓ Successfully downloaded {dest_path} ({len(content)} bytes)")
            return True
            
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {url}")
            if e.code == 404:
                print(f"   File not found in repository: {source_path}")
            return False
        except urllib.error.URLError as e:
            print(f"❌ URL Error: {e.reason}")
            return False
        except Exception as e:
            print(f"❌ Error downloading {source_path}: {str(e)}")
            return False
    
    def copy_files(self, files_config: List[Dict], force: bool = False) -> Tuple[int, int]:
        """
        Copy multiple files from configuration
        
        Args:
            files_config: List of dicts with 'source' and 'dest' keys
            force: Overwrite existing files
        
        Returns:
            Tuple of (success_count, total_count)
        """
        success_count = 0
        total_count = len(files_config)
        
        print(f"\n{'='*60}")
        print(f"Copying {total_count} file(s) from {self.source_repo}/{self.branch}")
        print(f"{'='*60}\n")
        
        for config in files_config:
            source = config.get('source')
            dest = config.get('dest')
            
            if not source or not dest:
                print(f"⚠️  Invalid config: {config}")
                continue
                
            if self.download_file(source, dest, force):
                success_count += 1
                
            print()  # Empty line for readability
        
        print(f"{'='*60}")
        print(f"✅ {success_count}/{total_count} files copied successfully")
        print(f"{'='*60}")
        
        return success_count, total_count
    
    def copy_from_json(self, json_file: str, force: bool = False) -> Tuple[int, int]:
        """
        Copy files using JSON configuration file
        
        Args:
            json_file: Path to JSON configuration file
            force: Overwrite existing files
        
        Returns:
            Tuple of (success_count, total_count)
        """
        try:
            with open(json_file, 'r') as f:
                config_data = json.load(f)
            
            # Support both direct array and object with 'files' key
            if isinstance(config_data, dict):
                files_config = config_data.get('files', [])
                # Override source repo if specified in JSON
                if 'source_repo' in config_data:
                    self.source_repo = self._parse_repo_url(config_data['source_repo'])
                    self.base_raw_url = f"https://raw.githubusercontent.com/{self.source_repo}/{self.branch}"
                if 'branch' in config_data:
                    self.branch = config_data['branch']
                    self.base_raw_url = f"https://raw.githubusercontent.com/{self.source_repo}/{self.branch}"
            else:
                files_config = config_data
                
            return self.copy_files(files_config, force)
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON file: {e}")
            return 0, 0
        except FileNotFoundError:
            print(f"❌ File not found: {json_file}")
            return 0, 0


def load_config_from_file(config_file: str) -> Dict:
    """Load configuration from file (JSON format)"""
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description='Copy files from one GitHub repository to another using raw URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Copy single file
  python copy_repo_files.py -s Samo1408/Builder_kernel -b m32-new -f fs/exec.c -d kernel_root/fs/exec.c
  
  # Copy multiple files using JSON config
  python copy_repo_files.py -c config.json --force
  
  # Copy files with different branch
  python copy_repo_files.py -s Samo1408/Builder_kernel -b main -c files_list.json

JSON Config Format:
  {
    "source_repo": "Samo1408/Builder_kernel",
    "branch": "m32-new",
    "files": [
      {"source": "fs/exec.c", "dest": "kernel_root/fs/exec.c"},
      {"source": "fs/open.c", "dest": "kernel_root/fs/open.c"},
      {"source": "kernel/reboot.c", "dest": "kernel_root/kernel/reboot.c"},
      {"source": "build.sh", "dest": "kernel_root/build.sh"}
    ]
  }
        """
    )
    
    parser.add_argument('-s', '--source', help='Source repository (username/repo or full URL)')
    parser.add_argument('-b', '--branch', default='main', help='Branch name (default: main)')
    parser.add_argument('-f', '--file', help='Single file source path')
    parser.add_argument('-d', '--dest', help='Single file destination path')
    parser.add_argument('-c', '--config', help='JSON configuration file for multiple files')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be copied without actual download')
    
    args = parser.parse_args()
    
    # Handle single file copy
    if args.file and args.dest:
        if args.dry_run:
            print(f"[DRY RUN] Would copy: {args.file} -> {args.dest}")
            return 0
            
        copier = FileCopier(args.source, args.branch)
        success, _ = copier.copy_files([{'source': args.file, 'dest': args.dest}], args.force)
        return 0 if success > 0 else 1
    
    # Handle config file copy
    elif args.config:
        if args.dry_run:
            print(f"[DRY RUN] Would copy files from config: {args.config}")
            # Load and show what would be copied
            try:
                with open(args.config, 'r') as f:
                    config = json.load(f)
                files = config.get('files', config) if isinstance(config, dict) else config
                for f in files:
                    print(f"  {f.get('source')} -> {f.get('dest')}")
            except:
                pass
            return 0
            
        copier = FileCopier(args.source if args.source else "", args.branch)
        success, total = copier.copy_from_json(args.config, args.force)
        return 0 if success == total else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())