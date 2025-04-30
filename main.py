#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
import docker

VOLUME_DIR = '/var/lib/docker/volumes'

def confirm(prompt):
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer == 'y'


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

    if not os.path.isdir(old_path):
        print(f"Error: Volume directory {old_path} does not exist.", file=sys.stderr)
        sys.exit(1)
    if os.path.exists(new_path):
        print(f"Error: Target path {new_path} already exists.", file=sys.stderr)
        sys.exit(1)

    client = docker.from_env()

    affected = []  # list of containers using the volume
    running_before = {}  # track which were running
    for container in client.containers.list(all=True):
        for mount in container.attrs.get('Mounts', []):
            if mount.get('Name') == old_vol or mount.get('Source', '').startswith(old_path):
                affected.append(container)
                running_before[container.id] = (container.status == 'running')
                break

    if affected:
        names = ', '.join(c.name for c in affected)
        print(f"Affected containers: {names}")
        if not args.force:
            if not confirm("Stop these containers?"):
                print("Aborted.")
                sys.exit(0)
        for container in affected:
            if running_before.get(container.id):
                print(f"Stopping container {container.name}...")
                try:
                    container.stop()
                except Exception as e:
                    print(f"Error stopping {container.name}: {e}", file=sys.stderr)

    # Rename the volume directory
    if not args.force:
        if not confirm(f"Rename directory {old_path} → {new_path}?"):
            print("Aborted.")
            sys.exit(0)
    print(f"Renaming {old_path} → {new_path}")
    shutil.move(old_path, new_path)

    # Adjust the `_data` symlink if it points to the old name
    data_link = os.path.join(new_path, '_data')
    if os.path.islink(data_link):
        target = os.readlink(data_link)
        if old_vol in target:
            new_target = target.replace(old_vol, new_vol)
            if not args.force:
                if not confirm(f"Update symlink target from {target} → {new_target}?"):
                    print("Left `_data` symlink unchanged.")
                    return
            print(f"Updating symlink to {new_target}")
            os.remove(data_link)
            os.symlink(new_target, data_link)

    # Restart previously running containers
    if affected:
        print("Starting previously running containers...")
        for container in affected:
            if running_before.get(container.id):
                print(f"Starting container {container.name}...")
                try:
                    container.start()
                except Exception as e:
                    print(f"Error starting {container.name}: {e}", file=sys.stderr)

    print("Done.")


if __name__ == '__main__':
    main()
