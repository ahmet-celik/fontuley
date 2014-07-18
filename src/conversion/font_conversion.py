
import webapp2
import sys, os
import StringIO

# Manually adding the library path seems hacky.
sys.path.append(os.path.join(os.path.dirname(__file__), '../third_party/fontTools/Lib'))
from fontTools.ttLib import TTFont

import cgi
import urllib


class FontConversionMainPage(webapp2.RequestHandler):


    def get(self):
        self.response.out.write('<html><body>')
 
        err_msg = self.request.get('err_msg') or ''
        if err_msg:
            self.response.out.write("""
                <div style='font-size: 200%%; font-weight:bold; color:red;'>%s
                </div>""" % err_msg)
 
        self.response.out.write('font conversion main page<br><br>')
 
        self.response.out.write("""
              <form enctype="multipart/form-data" method="post" action="font_conversion">Font:
                <input type="file" name="font"/><br>
                <br>""")
        self.conversion_options()

        self.response.out.write("""
                <br>
                <input type="submit" value="convert">
                <hr>
              </form>""")
 
        self.response.out.write('</body></html>')


    def conversion_options(self):
        self.response.out.write("""
                Convert to:
                <select name="conversion_to">
                  <option selected="selected">woff</option>
                  <option>ttf</option>
                </select>
                <br>""")


class FontConversion(webapp2.RequestHandler):

    def get(self):
      self.redirect('/font_conversion.html')


    def post(self):
        fontdata = self.request.POST.get('font', None)

        # Need to use isinstance as cgi.FieldStorage always evaluates to False.
        # See http://bugs.python.org/issue19097
        if not isinstance(fontdata, cgi.FieldStorage):
            self.redirect('/font_conversion.html?' +  urllib.urlencode(
                {'err_msg': 'Please select a font'}))
            return

        #TODO(bstell) make this work correctly.
        font_type = 'woff'
        name = os.path.splitext(os.path.basename(fontdata.filename))[0]

        try:
            font = TTFont(fontdata.file)
        except:
            self.redirect('/font_conversion.html?' +  urllib.urlencode(
                {'err_msg': 'failed to parse font'}))
            return

        self.response.headers['Content-Type'] = 'application/font-woff'
        self.response.headers['Content-Disposition'] = \
            'attachment; filename={0}.{1}'.format(name, font_type)
        font.flavor = font_type
        output = StringIO.StringIO()
        font.save(output)
        self.response.out.write(output.getvalue())




app = webapp2.WSGIApplication([
  ('/font_conversion.html', FontConversionMainPage),
  ('/font_conversion/?', FontConversion),
], debug=True)
