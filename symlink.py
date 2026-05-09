#!/usr/bin/env python3
"""
Script to create symbolic links (symlinks) for files and folders
Supports relative and absolute paths, with force option and dry-run mode
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Tuple, Optional

class SymlinkCreator:
    def __init__(self, force: bool = False, dry_run: bool = False):
        """
        Initialize the symlink creator
        
        Args:
            force: Force overwrite existing symlinks/files
            dry_run: Show what would be done without actually doing it
        """
        self.force = force
        self.dry_run = dry_run
        self.success_count = 0
        self.fail_count = 0
    
    def create_symlink(self, target: str, link_name: str, use_relative: bool = True) -> Tuple[bool, str]:
        """
        Create a symbolic link
        
        Args:
            target: Target file/folder to link to
            link_name: Name/path of the symlink to create
            use_relative: Use relative path instead of absolute
            
        Returns:
            Tuple of (success, message)
        """
        # Convert to Path objects
        target_path = Path(target).expanduser().resolve() if not use_relative else Path(target)
        link_path = Path(link_name).expanduser().resolve()
        
        # Check if target exists
        if not target_path.exists():
            return False, f"Target does not exist: {target_path}"
        
        # If using relative paths, calculate relative path from link directory to target
        if use_relative:
            try:
                # Get the directory where the symlink will be created
                link_dir = link_path.parent
                # Calculate relative path from link_dir to target
                relative_path = os.path.relpath(target_path, link_dir)
                final_target = relative_path
            except Exception as e:
                return False, f"Failed to calculate relative path: {e}"
        else:
            final_target = str(target_path)
        
        # Create parent directories if needed
        try:
            link_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Failed to create parent directories: {e}"
        
        # Check if link already exists
        if link_path.exists() or link_path.is_symlink():
            if not self.force:
                return False, f"Link already exists: {link_name} (use --force to overwrite)"
            
            if self.dry_run:
                return True, f"[DRY RUN] Would remove and recreate: {link_name} -> {final_target}"
            
            # Remove existing link/file
            try:
                if link_path.is_symlink() or link_path.is_file():
                    link_path.unlink()
                elif link_path.is_dir():
                    # Don't remove directories automatically for safety
                    return False, f"Cannot overwrite directory: {link_name} (remove manually)"
            except Exception as e:
                return False, f"Failed to remove existing link: {e}"
        
        if self.dry_run:
            return True, f"[DRY RUN] Would create: {link_name} -> {final_target}"
        
        # Create the symlink
        try:
            os.symlink(final_target, str(link_path))
            return True, f"✓ Created: {link_name} -> {final_target}"
        except PermissionError:
            return False, f"Permission denied: {link_name}"
        except Exception as e:
            return False, f"Failed to create symlink: {e}"
    
    def create_from_config(self, config_file: str) -> None:
        """
        Create symlinks from a JSON configuration file
        
        Args:
            config_file: Path to JSON configuration file
        """
        import json
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {config_file}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return
        
        symlinks = config.get('symlinks', [])
        use_relative = config.get('use_relative', True)
        
        print(f"\n{'='*60}")
        print(f"Creating {len(symlinks)} symlink(s) from config: {config_file}")
        print(f"Relative paths: {'Yes' if use_relative else 'No'}")
        print(f"Force mode: {'Yes' if self.force else 'No'}")
        print(f"{'='*60}\n")
        
        for item in symlinks:
            target = item.get('target')
            link = item.get('link')
            relative = item.get('relative', use_relative)
            
            if not target or not link:
                print(f"⚠️  Invalid config item: {item}")
                continue
            
            success, message = self.create_symlink(target, link, relative)
            print(message)
            
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1
            print()
        
        self._print_summary()
    
    def create_multiple(self, symlinks_list: list, use_relative: bool = True) -> None:
        """
        Create multiple symlinks from a list
        
        Args:
            symlinks_list: List of tuples (target, link_name)
            use_relative: Use relative paths
        """
        print(f"\n{'='*60}")
        print(f"Creating {len(symlinks_list)} symlink(s)")
        print(f"Relative paths: {'Yes' if use_relative else 'No'}")
        print(f"Force mode: {'Yes' if self.force else 'No'}")
        print(f"{'='*60}\n")
        
        for target, link_name in symlinks_list:
            success, message = self.create_symlink(target, link_name, use_relative)
            print(message)
            
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1
            print()
        
        self._print_summary()
    
    def _print_summary(self):
        """Print summary of operations"""
        print(f"{'='*60}")
        print(f"✅ Successful: {self.success_count}")
        print(f"❌ Failed: {self.fail_count}")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Create symbolic links (symlinks) easily',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a symlink (automatically uses relative paths)
  python symlink_creator.py -t /path/to/target -l /path/to/link
  
  # Force overwrite existing symlink
  python symlink_creator.py -t /path/to/target -l /path/to/link --force
  
  # Use absolute path instead of relative
  python symlink_creator.py -t /path/to/target -l /path/to/link --absolute
  
  # Dry run (preview only)
  python symlink_creator.py -t /path/to/target -l /path/to/link --dry-run
  
  # Create multiple symlinks
  python symlink_creator.py -m target1:link1 target2:link2 target3:link3
  
  # Use JSON config file
  python symlink_creator.py -c symlinks.json

JSON Config Format (symlinks.json):
  {
    "use_relative": true,
    "symlinks": [
      {"target": "../../KernelSU-Next/kernel", "link": "kernel_root/drivers/kernelsu", "relative": true},
      {"target": "../Builder_kernel/fs", "link": "kernel_root/fs", "relative": true},
      {"target": "/absolute/path/to/file", "link": "local/file", "relative": false}
    ]
  }
        """
    )
    
    parser.add_argument('-t', '--target', help='Target file/folder to link to')
    parser.add_argument('-l', '--link', help='Symlink name/path to create')
    parser.add_argument('-m', '--multiple', nargs='+', 
                        help='Multiple symlinks in format target:link (e.g., target1:link1 target2:link2)')
    parser.add_argument('-c', '--config', help='JSON configuration file')
    parser.add_argument('--absolute', action='store_true', 
                        help='Use absolute paths instead of relative (default: relative)')
    parser.add_argument('--force', action='store_true', 
                        help='Force overwrite existing symlinks/files')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be done without actually doing it')
    
    args = parser.parse_args()
    
    # Create symlink creator instance
    creator = SymlinkCreator(force=args.force, dry_run=args.dry_run)
    use_relative = not args.absolute
    
    # Handle single symlink
    if args.target and args.link:
        success, message = creator.create_symlink(args.target, args.link, use_relative)
        print(message)
        return 0 if success else 1
    
    # Handle multiple symlinks
    elif args.multiple:
        symlinks = []
        for item in args.multiple:
            if ':' not in item:
                print(f"❌ Invalid format: {item} (use target:link)")
                return 1
            target, link = item.split(':', 1)
            symlinks.append((target, link))
        
        creator.create_multiple(symlinks, use_relative)
        return 0 if creator.fail_count == 0 else 1
    
    # Handle config file
    elif args.config:
        creator.create_from_config(args.config)
        return 0 if creator.fail_count == 0 else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())