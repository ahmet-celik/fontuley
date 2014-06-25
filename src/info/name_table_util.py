
_name_ids = {
    0: { 'short': 'Copyright', 'name': 'Copyright notice' }, 
    1: { 'short': 'Family', 'name': 'Font Family name' }, 
    2: { 'short': 'Subfamily', 'name': 'Font Subfamily name' }, 
    3: { 'short': 'Unique ID', 'name': 'Unique font identifier' }, 
    4: { 'short': 'Full name', 'name': 'Full font name' }, 
    5: { 'short': 'Version', 'name': 'Version string' }, 
    6: { 'short': 'PS name', 'name': 'Postscript name' }, 
    7: { 'short': 'Trademark', 'name': 'Trademark' }, 
    8: { 'short': 'Manufacturer', 'name': 'Manufacturer Name' }, 
    9: { 'short': 'Designer', 'name': 'Designer' }, 
    10: { 'short': 'Desc.', 'name': 'Description' }, 
    11: { 'short': 'Vendor URL', 'name': 'URL Vendor' }, 
    12: { 'short': 'Designer URL', 'name': 'URL Designer' }, 
    13: { 'short': 'License', 'name': 'License Description' }, 
    14: { 'short': 'License URL', 'name': 'License Info URL' }, 
    15: { 'short': 'Reserved', 'name': 'Reserved' }, 
    16: { 'short': 'Preferred Fam', 'name': 'Preferred Family' }, 
    17: { 'short': 'Preferred Subfam', 'name': 'Preferred Subfamily' }, 
    18: { 'short': 'Compatible', 'name': 'Compatible Full' }, 
    19: { 'short': 'Sample text', 'name': 'Sample text' }, 
    20: { 'short': 'CID', 'name': 'PostScript CID' }, 
    21: { 'short': 'WWS Family', 'name': 'WWS Family Name' }, 
    21: { 'short': 'WWS Subfamily', 'name': 'WWS Subfamily Name' }
}

def name_id_to_name(name_id):
  info = _name_ids.get(name_id, { 'name': ''})
  return info['name']

def name_id_to_short_name(name_id):
  info = _name_ids.get(name_id, { 'short': ''})
  return info['short']

