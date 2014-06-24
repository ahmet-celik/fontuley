
import webapp2
from fontTools.ttLib import TTFont
import cgi
# import StringIO
import urllib


class MainPage(webapp2.RequestHandler):
    
    
    def get(self):
        self.response.out.write('<html><body>')

        err_msg = self.request.get('err_msg') or ''
        if err_msg:
            self.response.out.write("""
                <div style='font-size: 200%%; font-weight:bold; color:red;'>%s
                </div>""" % err_msg)

        self.response.out.write("""
              <form enctype="multipart/form-data" method="post" action="font_info">Font:
                <input type="file" name="font"/>
                <input type="submit" value="upload">
              </form>""")

        self.response.out.write('</body></html>')


class FontInfo(webapp2.RequestHandler):

    def post(self):
        self.response.out.write("""<html>
            <head>
              <link rel="stylesheet" type="text/css" href="css/styles.css">
            </head>
            <body>""")

        fontdata = self.request.POST['font']
        # Need to use isinstance as cgi.FieldStorage always evaluates to False.
        # See http://bugs.python.org/issue19097
        if not isinstance(fontdata, cgi.FieldStorage):
            self.redirect('/?' +  urllib.urlencode(
                {'err_msg': 'Please select a font'}))
            return
        self.response.out.write(fontdata.filename + '<br>')
        try:
            font = TTFont(fontdata.file)
        except:
            self.redirect('/?' +  urllib.urlencode(
                {'err_msg': 'failed to parse font'}))
            return

        self.response.out.write("""<table><tr>
            <th>Table</th><th>Offset</th><th>Length</th></tr>""")

        tables = font.reader.tables
        for tag in tables:
          table = tables[tag]
          self.response.out.write("""<tr>
              <td style='text-align: center'>{0}</td><td>{1}</td><td>{2}</td></tr>"""
              .format(tag, table.offset, table.length))

        self.response.out.write('</table>')


        self.response.out.write('</body></html>')


app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/font_info', FontInfo),
], debug=True)
