
import webapp2


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



app = webapp2.WSGIApplication([
  ('/', MainPage),
], debug=True)
