
import binascii
import webapp2
import sys, os

# Manually adding the library path seems hacky.
sys.path.append(os.path.join(os.path.dirname(__file__), '../third_party/fontTools/Lib'))
from fontTools.ttLib import TTFont

import cgi
import urllib
import unicodedata


class FontInfoMainPage(webapp2.RequestHandler):


    def get(self):
        self.response.out.write('<html><body>')
 
        err_msg = self.request.get('err_msg') or ''
        if err_msg:
            self.response.out.write("""
                <div style='font-size: 200%%; font-weight:bold; color:red;'>%s
                </div>""" % err_msg)
 
        self.response.out.write('font info main page<br><br>')
 
        self.response.out.write("""
              <form enctype="multipart/form-data" method="post" action="font_info">Font:
                <input type="file" name="font"/><br>
                <br>""")
        self.tables_options()
        self.cmap_options()
        self.name_table_options()

        self.response.out.write("""
                <br>
                <input type="submit" value="get info">
                <hr>
              </form>""")
 
        self.response.out.write('</body></html>')


    def tables_options(self):
        self.response.out.write("""
                Table Of Contents:
                <input type="checkbox" name="tables_checkbox"> 
                sort by:
                <select name="tables_sort">
                  <option selected="selected">table</option>
                  <option>offset</option>
                  <option>length</option>
                </select>
                <br>""")

    def cmap_options(self):
        self.response.out.write("""
                cmap:
                <input type="checkbox" name="cmap_checkbox"> 
                cmap segment info:
                <input type="checkbox" name="cmap_segments"> 
                <select name="cmap_platformID">
                  <option value="" selected="selected">All</option>
                  <option value="0">Apple</option>
                  <option value="1">Apple Script Manager</option>
                  <option value="2">ISO</option>
                  <option value="3">Windows</option>
                </select>
                <br>""")

    def name_table_options(self):
        # license is nameID=13 in the name table
        self.response.out.write("""
                name table:
                <input type="checkbox" name="name_table_checkbox"> 
                <br>""")
        pass

class FontInfo(webapp2.RequestHandler):

    def get(self):
      self.redirect('/font_info.html')


    def post(self):
        fontdata = self.request.POST.get('font', None)

        # Need to use isinstance as cgi.FieldStorage always evaluates to False.
        # See http://bugs.python.org/issue19097
        if not isinstance(fontdata, cgi.FieldStorage):
            self.redirect('/font_info.html?' +  urllib.urlencode(
                {'err_msg': 'Please select a font'}))
            return

        try:
            font = TTFont(fontdata.file)
        except:
            self.redirect('/font_info.html?' +  urllib.urlencode(
                {'err_msg': 'failed to parse font'}))
            return

        self.response.out.write("""<html>
            <head>
              <meta charset="UTF-8">
              <link rel="stylesheet" type="text/css" href="css/styles.css">
            </head>
            <body>
              Font Info: {0}<br><br>""".format(fontdata.filename))

        self.tables_info(font)
        self.cmap_info(font)
        self.name_table_info(font)

        self.response.out.write('</body></html>')


    def tables_info(self, font):
        tables_checkbox = self.request.POST.get('tables_checkbox', None)
        if not tables_checkbox:
            return
        tables_sort = self.request.POST.get('tables_sort', None)
        self.response.out.write("""Table Of Contents<br>
            <table><tr><th>Table</th><th>Offset</th><th>Length</th></tr>""")

        tables = font.reader.tables
        sorted_tables = []
        if tables_sort == 'offset':
          sorted_tables = sorted(tables, key=lambda tag: tables[tag].offset)
        elif tables_sort == 'length':
          sorted_tables = sorted(tables, key=lambda tag: tables[tag].length)
        else:
          sorted_tables = sorted(tables)
        
        for tag in sorted_tables:
          table = tables[tag]
          self.response.out.write("""<tr>
              <td style='text-align: center'>{0}</td><td>{1}</td><td>{2}</td></tr>"""
              .format(tag, table.offset, table.length))

        self.response.out.write('</table><br><br>')


    def cmap_info(self, font):
        cmap_checkbox = self.request.POST.get('cmap_checkbox', None)
        if not cmap_checkbox:
            return
        cmap_platformID = self.request.POST.get('cmap_platformID', None)
        if cmap_platformID == None or cmap_platformID == '':
            cmap_platformID = None
        else:
            cmap_platformID = int(cmap_platformID)
            self.response.out.write('only show cmaps for platformID={0}<br><br>'.
                                    format(cmap_platformID))

        
        self.response.out.write("""cmap segments<br>
            <table><tr>
              <th>platformID</th>
              <th>platEncID</th>
              <th>format</th>
              <th>length</th>
            </tr>""")

        cmap = font['cmap']
        for i in range(len(cmap.tables)):
            table = cmap.tables[i]
            self.response.out.write("""<tr>
                  <td >{0}</td><td>{1}</td><td>{2}</td><td>{3}</td>
                </tr>""".format(table.platformID, table.platEncID, table.format, 
                                table.length))
        self.response.out.write('</table><br><br>')

        cmap_segments = self.request.POST.get('cmap_segments', None)
        if not cmap_segments:
            return

        # Find format 12 character ranges:
        # - contiguous code points _and_ contiguous glyph IDs
        glyphOrder = font.getGlyphOrder()
        for i in range(len(cmap.tables)):
            table = cmap.tables[i]
            if cmap_platformID != None:
                if table.platformID != cmap_platformID:
                    continue
            self.response.out.write(
                """cmap: platfromID={0}, encodingID={1}, format={2}<br>"""
                .format(table.platformID, table.platEncID, table.format))
            submap = cmap.getcmap(table.platformID, table.platEncID)
            items = sorted(submap.cmap.items(), key=lambda item: item[0])
            start_code = previous_code = None
            start_gid = previous_gid = None
            segments = []

            sub_segments = 0
            for item in items:
                this_code = item[0]
                this_gid = glyphOrder.index(item[1])
                if start_code == None:
                    start_code = previous_code = this_code
                    start_gid = previous_gid = this_gid
                    continue
                if this_code == previous_code + 1:
                    if this_gid != previous_gid + 1:
                        sub_segments += 1
                    previous_code = this_code
                    previous_gid = this_gid
                    continue
                sub_segments += 1
                segments.append({'start_code': start_code, 
                                 'end_code': previous_code,
                                 'start_gid': start_gid,
                                 'length': previous_code - start_code + 1,
                                 'sub_segments': sub_segments,
                                 })
                start_code = previous_code = this_code
                start_gid = previous_gid = this_gid
                sub_segments = 0

            # Close the final range.
            if start_code != None:
                sub_segments += 1
                segments.append({'start_code': start_code, 
                                 'end_code': previous_code,
                                 'start_gid': start_gid,
                                 'length': previous_code - start_code + 1,
                                 'sub_segments': sub_segments,
                                 })



            # Display the results.
            # Note: we only need a usable format 12 (format 4 can be a dummy)
            total_codepoints = 0
            total_sub_segments = 0
            table_str = """<table><tr>
                  <th>start code</th>
                  <th>gid</th>
                  <th>length</th>
                  <th>segments</th>
                  <th>Description</th>
                </tr>"""
            for segment in segments:
                start_code = segment['start_code']
                length = segment['length']
                total_codepoints += length
                table_str += """<tr>
                    <td >0x{0:05X}</td><td>{1}</td><td>{2}</td><td>{3}</td>
                    <td style="text-align: left">{4}</td>
                    </tr>""".format(
                    start_code, segment['start_gid'], length, 
                    segment['sub_segments'], 
                    get_unicode_name(segment['start_code']))
                total_sub_segments += segment['sub_segments']
            table_str += '</table><br><br>'
            self.response.out.write('{0} total codepoints<br>'.format(total_codepoints))
            self.response.out.write('{0} contiguous character segments<br>'.format(len(segments)))
            self.response.out.write('{0} segments required<br>'.format(total_sub_segments))
            self.response.out.write(table_str)


    def name_table_info(self, font):
        name_table_checkbox = self.request.POST.get('name_table_checkbox', None)
        if not name_table_checkbox:
            return
#===============================================================================
#         cmap_platformID = self.request.POST.get('cmap_platformID', None)
#         if cmap_platformID == None or cmap_platformID == '':
#             cmap_platformID = None
#         else:
#             cmap_platformID = int(cmap_platformID)
#             self.response.out.write('only show cmaps for platformID={0}<br><br>'.
#                                     format(cmap_platformID))
# 
#         
        self.response.out.write("""name table:<br>
            <table><tr>
              <th>langID</th>
              <th>nameID</th>
              <th>platformID</th>
              <th>platEncID</th>
              <th>string</th>
            </tr>""")

        name_table = font['name']
        for name in name_table.names:
            if not name.isUnicode():
                continue
            hexstr = name.string
            if len(hexstr) %2:
                hexstr += b"\0"
            utf16str = hexstr.decode('utf-16-be')
            utf8str = utf16str.encode('UTF-8')
            self.response.out.write("""<tr>
                  <td >{0}</td>
                  <td>{1}</td>
                  <td>{2}</td>
                  <td>{3}</td>
                  <td>{4}</td>
                </tr>""".format(name.langID,
                                name.nameID,
                                name.platformID,
                                name.platEncID,
                                utf8str))
        self.response.out.write('</table><br><br>')
# 
#         cmap_segments = self.request.POST.get('cmap_segments', None)
#         if not cmap_segments:
#             return
# 
#         # Find format 12 character ranges:
#         # - contiguous code points _and_ contiguous glyph IDs
#         glyphOrder = font.getGlyphOrder()
#         for i in range(len(cmap.tables)):
#             table = cmap.tables[i]
#             if cmap_platformID != None:
#                 if table.platformID != cmap_platformID:
#                     continue
#             self.response.out.write(
#                 """cmap: platfromID={0}, encodingID={1}, format={2}<br>"""
#                 .format(table.platformID, table.platEncID, table.format))
#             submap = cmap.getcmap(table.platformID, table.platEncID)
#             items = sorted(submap.cmap.items(), key=lambda item: item[0])
#             start_code = previous_code = None
#             start_gid = previous_gid = None
#             segments = []
# 
#             sub_segments = 0
#             for item in items:
#                 this_code = item[0]
#                 this_gid = glyphOrder.index(item[1])
#                 if start_code == None:
#                     start_code = previous_code = this_code
#                     start_gid = previous_gid = this_gid
#                     continue
#                 if this_code == previous_code + 1:
#                     if this_gid != previous_gid + 1:
#                         sub_segments += 1
#                     previous_code = this_code
#                     previous_gid = this_gid
#                     continue
#                 sub_segments += 1
#                 segments.append({'start_code': start_code, 
#                                  'end_code': previous_code,
#                                  'start_gid': start_gid,
#                                  'length': previous_code - start_code + 1,
#                                  'sub_segments': sub_segments,
#                                  })
#                 start_code = previous_code = this_code
#                 start_gid = previous_gid = this_gid
#                 sub_segments = 0
# 
#             # Close the final range.
#             if start_code != None:
#                 sub_segments += 1
#                 segments.append({'start_code': start_code, 
#                                  'end_code': previous_code,
#                                  'start_gid': start_gid,
#                                  'length': previous_code - start_code + 1,
#                                  'sub_segments': sub_segments,
#                                  })
# 
# 
# 
#             # Display the results.
#             # Note: we only need a usable format 12 (format 4 can be a dummy)
#             total_codepoints = 0
#             total_sub_segments = 0
#             table_str = """<table><tr>
#                   <th>start code</th>
#                   <th>gid</th>
#                   <th>length</th>
#                   <th>segments</th>
#                   <th>Description</th>
#                 </tr>"""
#             for segment in segments:
#                 start_code = segment['start_code']
#                 length = segment['length']
#                 total_codepoints += length
#                 table_str += """<tr>
#                     <td >0x{0:05X}</td><td>{1}</td><td>{2}</td><td>{3}</td>
#                     <td style="text-align: left">{4}</td>
#                     </tr>""".format(
#                     start_code, segment['start_gid'], length, 
#                     segment['sub_segments'], 
#                     get_unicode_name(segment['start_code']))
#                 total_sub_segments += segment['sub_segments']
#             table_str += '</table><br><br>'
#             self.response.out.write('{0} total codepoints<br>'.format(total_codepoints))
#             self.response.out.write('{0} contiguous character segments<br>'.format(len(segments)))
#             self.response.out.write('{0} segments required<br>'.format(total_sub_segments))
#             self.response.out.write(table_str)
#===============================================================================


def get_unicode_name(code):
    try:
        return unicodedata.name(unichr(code))
    except ValueError:
        return '&lt;unknown&gt;'


app = webapp2.WSGIApplication([
  ('/font_info.html', FontInfoMainPage),
  ('/font_info/?', FontInfo),
], debug=True)
