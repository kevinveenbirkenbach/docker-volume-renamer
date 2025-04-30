#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
import docker

VOLUME_DIR = '/var/lib/docker/volumes'

def confirm(prompt):
    ans = input(f"{prompt} [Y/n]: ").strip().lower()
    return ans in ('', 'y', 'yes')

def main():
    parser = argparse.ArgumentParser(
        description="Rename a Docker volume directory and optionally stop & restart affected containers."
    )
    parser.add_argument('old', help="Old volume name")
    parser.add_argument('new', help="New volume name")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Skip all confirmation prompts")
    args = parser.parse_args()

    old_vol = args.old
    new_vol = args.new
    old_path = os.path.join(VOLUME_DIR, old_vol)
    new_path = os.path.join(VOLUME_DIR, new_vol)

    # Validate volume paths
    if not os.path.isdir(old_path):
        print(f"Error: Volume directory {old_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    if os.path.exists(new_path):
        print(f"Error: Target path {new_path} already exists.", file=sys.stderr)
        sys.exit(1)

    client = docker.from_env()

    # Find containers using the old volume
    affected = []            # list of containers using the volume
    running_before = {}      # track which were running
    for container in client.containers.list(all=True):
        for mount in container.attrs.get('Mounts', []):
            if mount.get('Name') == old_vol or mount.get('Source', '').startswith(old_path):
                affected.append(container)
                running_before[container.id] = (container.status == 'running')
                break

    # Stop affected containers
    if affected:
        print(f"Affected containers: {', '.join(c.name for c in affected)}")
        if not args.force:
            if not confirm("Stop these containers?"):
                print("Aborted before stopping containers.")
                sys.exit(0)
        for container in affected:
            if running_before.get(container.id):
                if not args.force:
                    if not confirm(f"Confirm stopping container {container.name}?" ):
                        print(f"Skipping stop for {container.name}.")
                        continue
                print(f"Stopping container {container.name}...")
                try:
                    container.stop()
                except Exception as e:
                    print(f"Error stopping {container.name}: {e}", file=sys.stderr)

    # Rename the volume directory
    if not args.force:
        if not confirm(f"Rename directory {old_path} → {new_path}?" ):
            print("Aborted before renaming volume directory.")
            sys.exit(0)
    print(f"Renaming {old_path} → {new_path}")
    shutil.move(old_path, new_path)

    # Remove old Docker volume
    try:
        if not args.force:
            if confirm(f"Remove Docker volume '{old_vol}' from Docker?" ):
                client.volumes.get(old_vol).remove()
                print(f"Removed Docker volume '{old_vol}'.")
            else:
                print(f"Skipped removing Docker volume '{old_vol}'.")
        else:
            client.volumes.get(old_vol).remove()
            print(f"Removed Docker volume '{old_vol}'.")
    except docker.errors.NotFound:
        print(f"Docker volume '{old_vol}' not found.")
    except Exception as e:
        print(f"Error removing Docker volume '{old_vol}': {e}", file=sys.stderr)

    # Handle _data symlink: rename target folder and update link
    data_link = os.path.join(new_path, '_data')
    if os.path.islink(data_link):
        original_target = os.readlink(data_link)
        if old_vol in original_target:
            updated_target = original_target.replace(old_vol, new_vol)
            # Rename the symlink's target folder
            if os.path.isdir(original_target):
                if not args.force:
                    if confirm(f"Rename target folder {original_target} → {updated_target}?" ):
                        print(f"Renaming target folder {original_target} → {updated_target}")
                        shutil.move(original_target, updated_target)
                    else:
                        print(f"Skipped renaming target folder {original_target}.")
                else:
                    print(f"Renaming target folder {original_target} → {updated_target}")
                    shutil.move(original_target, updated_target)
                # Only update link if folder was renamed or even if skipped to maintain consistency
                original_target = updated_target
            # Update the symlink
            if not args.force:
                if confirm(f"Update `_data` symlink to point to {original_target}?" ):
                    print(f"Updating `_data` symlink to {original_target}")
                    os.remove(data_link)
                    os.symlink(original_target, data_link)
                else:
                    print("Skipped updating `_data` symlink.")
            else:
                print(f"Updating `_data` symlink to {original_target}")
                os.remove(data_link)
                os.symlink(original_target, data_link)

    # Warn and optionally restart containers
    if affected:
        warning_msg = (
            "WARNING: When containers restart, Docker may create a new anonymous volume "
            "for the original mount path if the container's configuration still points to it."
        )
        print(warning_msg)
        if not args.force:
            if not confirm("Restart previously running containers?"):
                print("Skipped restarting containers.")
                print("Done.")
                return
        for container in affected:
            if running_before.get(container.id):
                if not args.force:
                    if not confirm(f"Confirm restarting container {container.name}?" ):
                        print(f"Skipping restart for {container.name}.")
                        continue
                print(f"Starting container {container.name}...")
                try:
                    container.start()
                except Exception as e:
                    print(f"Error starting {container.name}: {e}", file=sys.stderr)

    print("Done.")

if __name__ == '__main__':
    main()

