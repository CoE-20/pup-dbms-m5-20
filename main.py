import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import os
import logging
import json
import urllib

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class User(ndb.Model):
    created_by = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    phone_number = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Thesis(ndb.Model):
    year = ndb.IntegerProperty()
    Title = ndb.StringProperty(indexed=True)
    abstract = ndb.TextProperty(indexed=True)
    adviser = ndb.StringProperty()
    section = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class DeleteEntry(webapp2.RequestHandler):
    def get(self, thesis_id):
        thesis = Thesis.get_by_id(int(thesis_id))
        thesis.key.delete()
        self.redirect('/')

class EditEntry(webapp2.RequestHandler):
    def get(self, thesis_id):
        thesis = Thesis.get_by_id(int(thesis_id))
        template_data = {
            'thesis': thesis
        }
        user = users.get_current_user()

        if user:

            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout,'  +  ' ' + users.get_current_user().nickname()
            status = 'Hello, '
            template_values = {
            'user': user,
            'status': status,
            'url': url,
            'url_linktext': url_linktext,
            }
        
        # template = JINJA_ENVIRONMENT.get_template('main.html')
        # self.response.write(template.render(template_values))
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_data))

    def post(self, thesis_id):
        
        thesis = Thesis.get_by_id(int(thesis_id))
        thesis.created_by = users.get_current_user().user_id()
        thesis.email = users.get_current_user().email()
        thesis.year = int(self.request.get('year'))
        thesis.Title = self.request.get('Title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = int(self.request.get('section'))
        thesis.put()
        self.redirect('/login')

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('main.html')
        
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout' + ' ' +  users.get_current_user().nickname()
            check = 1
            check1 = 1
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            check = 1
            check1 = 0

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'check': check,
            'check1': check1
        }
        self.response.write(template.render(template_values))

class RegisterPageHandler(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()
        if loggedin_user: 
            user_key = ndb.Key('User', loggedin_user.user_id())
            user = user_key.get()
            if user:
                url = users.create_logout_url('/register')
                url_linktext = 'Logout' +  ' ' + users.get_current_user().nickname()
                status = 'Hello, '
                template_values = {
                    'url': url,
                    'url_linktext': url_linktext,
                    'status' : status
                }
                self.redirect('/register')
            else:
                template = JINJA_ENVIRONMENT.get_template('registration.html')
                self.response.write(template.render())
        else:
            self.redirect(users.create_login_url('/register'))

    def post(self):

        user = User(id=users.get_current_user().user_id(), email= users.get_current_user().email(), first_name = self.request.get('first_name'), last_name = self.request.get('last_name'), phone_number = self.request.get('phone_number')) 
        user.put()
        self.redirect('/login')

class APIUserHandler(webapp2.RequestHandler):
    def get(self):
        users = User.query().order(-User.date).fetch()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.key.id(),
                'created_by': user.created_by,
                'email' : user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number':user.phone_number
                });
            
        response = {
             'result' : 'OK',
             'data' : user_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))
    def post(self):
        user = User()
       
        user.first_name = self.request.get('first_name')
        user.last_name = self.request.get('last_name')
        user.phone_number = self.request.get('phone_number')
        user.email = users.get_current_user().email()
        user.key = user.put()
        user.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
        'result' : 'OK',
        'data':{
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
        }
        }
        self.response.out.write(json.dumps(response))


class APIStudentHandler(webapp2.RequestHandler):
    def get(self):
        details = Thesis.query().order(-Thesis.date).fetch()
        detail_list = []

        for detail in details:
            detail_list.append({
                'id': detail.key.urlsafe(),
                'year': detail.year,
                'Title': detail.Title,
                'abstract': detail.abstract,
                'adviser': detail.adviser,
                'section': detail.section
            })

        response = {
            'result': 'OK',
            'data': detail_list
        }
        self.response.headers['Content-Type'] = 'application.json'        
        self.response.out.write(json.dumps(response))

    def post(self):
        detail = Thesis()
        detail.year = int(self.request.get('year'))
        detail.Title = self.request.get('Title')
        detail.abstract = self.request.get('abstract')
        detail.adviser = self.request.get('adviser')
        detail.section = int(self.request.get('section'))
        detail.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result': 'OK',
            'data': {
                'id': detail.key.urlsafe(),
                'year': detail.year,
                'Title': detail.Title,
                'abstract': detail.abstract,
                'adviser': detail.adviser,
                'section': detail.section,
            }
        }
        self.response.headers['Content-Type'] = 'application/json'        
        self.response.out.write(json.dumps(response))
  

app = webapp2.WSGIApplication([
    ('/api/thesis', APIStudentHandler),
    ('/api/user', APIUserHandler),
    ('/login', MainPageHandler),
    ('/register', RegisterPageHandler)
], debug=True)