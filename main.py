import webapp2
import jinja2
import httplib2
import os

from apiclient.discovery import build
from oauth2client.appengine import Oauth2DecoratorFromClientSecrets

#FLOW
JINJA_ENVIRONMENT = jinja2.Environment (
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True
)

decorator = Oauth2DecoratorFromClientSecrets(
    os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    scope = 'https://www.googleapis.com/auth/bigquery'
)
PROJECT_ID = 'plucky-vision-274711' #to communicate through the api

class MainPage (webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        country_region = self.request.get('country')

        template_values = {'rows': [], 'country': country_region}

        if country_region:
            query = {'query': ''' SELECT date, confirmed, deaths, active FROM [plucky-vision-274711.sasha.summary]
                                 WHERE country_region = "%s"
                                 ORDER BY active DESC
                                 LIMIT 10 '''}
            service = build('bigquery', 'v2', http=decorator.http())
            results = service.jobs().query(projectId=PROJECT_ID, body=query).execute()

            for row in results['rows']:
                fields = results['schema']['fields']
                template_values['rows'].append({
                    fields[i]['date']: row['f'][i]['v'] for i in xrange(len(fields))
                })

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
            ('/', MainPage),
            (decorator.callback_path, decorator.callback_handler())
        ], debug=True)