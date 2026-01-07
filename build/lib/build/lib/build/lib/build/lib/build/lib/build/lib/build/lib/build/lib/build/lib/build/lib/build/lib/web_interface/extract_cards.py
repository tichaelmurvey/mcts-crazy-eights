#!/usr/bin/env python3
"""
Extract individual card SVGs from the svg-cards.svg sprite sheet.
Creates separate SVG files for each card in the img/cards/ directory.
"""

import os
import re
from xml.etree import ElementTree as ET

# Card IDs to extract
SUITS = ['club', 'diamond', 'heart', 'spade']
VALUES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

# Card dimensions (from the base path in the SVG)
CARD_WIDTH = 167
CARD_HEIGHT = 243

def extract_cards():
    # Parse the source SVG
    source_path = 'img/svg-cards.svg'

    # Read the file content
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Register namespaces to preserve them
    namespaces = {
        '': 'http://www.w3.org/2000/svg',
        'xlink': 'http://www.w3.org/1999/xlink'
    }
    for prefix, uri in namespaces.items():
        if prefix:
            ET.register_namespace(prefix, uri)
        else:
            ET.register_namespace('', uri)

    tree = ET.parse(source_path)
    root = tree.getroot()

    # Create output directory
    output_dir = 'img/cards'
    os.makedirs(output_dir, exist_ok=True)

    # Find all elements with IDs
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    # Build list of card IDs to extract
    card_ids = []
    for suit in SUITS:
        for value in VALUES:
            card_ids.append(f"{value}_{suit}")
    card_ids.append('back')

    # Extract the defs section which contains shared elements
    defs = root.find('.//{http://www.w3.org/2000/svg}defs')

    for card_id in card_ids:
        # Find the element with this ID
        element = root.find(f".//*[@id='{card_id}']")

        if element is None:
            print(f"Warning: Could not find element with id '{card_id}'")
            continue

        # Create a new SVG document
        new_svg = ET.Element('svg')
        new_svg.set('xmlns', 'http://www.w3.org/2000/svg')
        new_svg.set('xmlns:xlink', 'http://www.w3.org/1999/xlink')
        new_svg.set('viewBox', f'0 0 {CARD_WIDTH} {CARD_HEIGHT}')
        new_svg.set('width', str(CARD_WIDTH))
        new_svg.set('height', str(CARD_HEIGHT))

        # Copy the defs section
        if defs is not None:
            new_svg.append(ET.fromstring(ET.tostring(defs)))

        # Create a group to transform the card to start at 0,0
        g = ET.SubElement(new_svg, 'g')
        g.set('transform', 'translate(0, 236)')

        # Copy the card element
        g.append(ET.fromstring(ET.tostring(element)))

        # Write to file
        output_path = os.path.join(output_dir, f'{card_id}.svg')
        tree = ET.ElementTree(new_svg)
        tree.write(output_path, encoding='unicode', xml_declaration=True)
        print(f"Created {output_path}")

    print(f"\nExtracted {len(card_ids)} cards to {output_dir}/")

if __name__ == '__main__':
    extract_cards()
