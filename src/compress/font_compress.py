import webapp2
import sys, os

# Manually adding the library path seems hacky.
sys.path.append(os.path.join(os.path.dirname(__file__), '../third_party/fontTools/Lib'))
from fontTools.ttLib import TTFont

import cgi
import urllib
class FontCompressMainPage(webapp2.RequestHandler):


    def get(self):
        self.response.out.write('<html><body>')
 
        err_msg = self.request.get('err_msg') or ''
        if err_msg:
            self.response.out.write("""
                <div style='font-size: 200%%; font-weight:bold; color:red;'>%s
                </div>""" % err_msg)
 
        self.response.out.write('font compress main page<br><br>')
 
        self.response.out.write("""
              <form enctype="multipart/form-data" method="post" action="font_compress">Font:
                <input type="file" name="font"/><br>
                <br>""")

        self.response.out.write("""
                <br>
                <input type="submit" value="compress font">
                <hr>
              </form>""")
 
        self.response.out.write('</body></html>')

class FontCompress(webapp2.RequestHandler):

    def get(self):
      self.redirect('/font_compress.html')


    def post(self):
        fontdata = self.request.POST.get('font', None)

        # Need to use isinstance as cgi.FieldStorage always evaluates to False.
        # See http://bugs.python.org/issue19097
        if not isinstance(fontdata, cgi.FieldStorage):
            self.redirect('/font_compress.html?' +  urllib.urlencode(
                {'err_msg': 'Please select a font'}))
            return

        try:
            font = TTFont(fontdata.file)
        except:
            self.redirect('/font_compress.html?' +  urllib.urlencode(
                {'err_msg': 'failed to parse font'}))
            return

        self.response.headers['Content-Type'] = 'application/octet-stream'
        font.flavor = 'woff'
        font.save('temp',reorderTables=False)
        tmp = open('temp')
        self.response.write(tmp.read())
        tmp.close()
        

app = webapp2.WSGIApplication([
  ('/font_compress.html', FontCompressMainPage),
  ('/font_compress/?', FontCompress),
], debug=True)