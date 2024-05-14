#!/usr/local/bin/python3

import os
import json
import hashlib
import shutil

base = os.path.dirname(os.path.abspath(__file__))

# config
manifest_path = os.path.join(base, 'server-manifest.json')
override_path = os.path.join(base, 'overrides')

detect_base = os.path.abspath('/Users/jessiezhu/Library/Application Support/minecraft/versions/CMIP')
override_contents = [
    'log4j2.xml',
	'ModTranslations',
	'config',
	'mods',
	'resourcepacks',
	'hmclversion.cfg'
]

override_ignore = [
	'.DS_Store',
	'desktop.ini',
	'System Volume Information',
	'Thumbs.db',
	'$RECYCLE.BIN',
	'.hmcl.json',
	'.config.ini',
	'autorun.inf'
]

manifest = {
	"name": "Createch Mod Integration Pack",
	"author": "CreatechStudio Shanghai Inc.",
	"version": "1.20.4b5b",
	"description": "",
	"fileApi": "https://mci.createchstudio.com",
	"files": {},
	"addons": [
		{
			"id": "game",
			"version": "1.20.4"
		},
		{
			"id": "fabric",
			"version": "0.15.11"
		}
	]
}

# funcs
def get_hash(p):
	sha1 = hashlib.sha1()
	with open(p, 'rb') as f:
		while True:
			data_bytes = f.read(128000)
			sha1.update(data_bytes)
			if not data_bytes:
				break
	return sha1.hexdigest()

def copy_file(original_path, p):
	shutil.copyfile(original_path, os.path.join(override_path, p))

def scan_dir(content_path, p):
	files = []

	current_override_path = os.path.join(override_path, p)

	if not os.path.exists(current_override_path):
		os.mkdir(current_override_path)

	for item in os.scandir(content_path):
		if item.is_dir():
			if item.name in override_ignore:
				continue
			files += scan_dir(item.path, os.path.join(p, item.name))
		if item.is_file():
			if item.name in override_ignore:
				continue
			files.append({
				'path': os.path.join(p, item.name),
				'hash': get_hash(item.path)
			})
			copy_file(item.path, os.path.join(p, item.name))

	return files

def new_files():
	files = []

	if os.path.exists(override_path):
		shutil.rmtree(override_path)
	os.mkdir(override_path)

	for content in override_contents:
		if content in override_ignore:
			continue

		content_path = os.path.join(detect_base, content)
		if os.path.exists(content_path):
			if os.path.isdir(content_path):
				files += scan_dir(content_path, content)
			if os.path.isfile(content_path):
				files.append({
					'path': content,
					'hash': get_hash(content_path)
				})
				parent_dir = os.path.dirname(os.path.join(override_path, content))
				if not os.path.exists(parent_dir):
					os.mkdir(parent_dir)
				copy_file(content_path, content)

	return files

# main
old_manifest = {}
if os.path.exists(manifest_path):
	with open(manifest_path, 'r') as f:
		old_manifest = json.loads(f.read())

if 'version' in old_manifest:
	if old_manifest['version'] == manifest['version']:
		print('[WARNING] Version does not change!')

manifest['files'] = new_files()

with open(manifest_path, 'w') as f:
	f.write(json.dumps(manifest, indent=2))

print(f'Current Version: {manifest["version"]}')
