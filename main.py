#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import re

from datetime import datetime
import webapp2
import logging
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from Template_Handler import Handler

from Users import Users
from Topics import Topics

from urlparse import urlparse

STREAMS = {"btechcse": "Btech CSE", "btechece": "Btech ECE"}
CATEGORIES = {"dsa": "Data Structure and Algorithms", "prog_langs": "Programming Languages"}

def get_user(email):
    u = db.GqlQuery("SELECT * FROM Users where email=:1 LIMIT 1", email)
    if u.count() == 1:
        return u.fetch(1)[0]

def checkUrl(url) :
    # django regex for url validation

    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.search(regex, url) == None :
        return 0
    else :
        return 1


class Home(Handler):
    def get(self):
        u = db.GqlQuery("SELECT * FROM Topics WHERE when != :1 ORDER BY when DESC LIMIT 3", None)
        recent = u.fetch(3)
        for r in recent:
            for student in range(0, len(r.list_of_students)):
                s = r.list_of_students[student]
                r.list_of_students[student] = db.get(s)
            for teacher in range(0, len(r.list_of_teachers)):
                s = r.list_of_teachers[teacher]
                r.list_of_teachers[teacher] = db.get(s)

        user = users.get_current_user()
        if user:
            self.render("index.html", recent=recent, user=user, logout_link=users.create_logout_url('/'))
        else:
            self.render("index.html", recent=recent)
class Register(Handler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_obj = get_user(user.email())
            if user_obj:
                self.redirect("/home")
            else:
                self.render('register.html', email=user.email(), streams=STREAMS)
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        user = users.get_current_user()
        name = self.request.get('name').strip()
        roll = self.request.get('roll').strip()
        stream = self.request.get('stream').strip()
        skills = self.request.get('skills').strip()
        skills_to_learn = self.request.get('skills_to_learn').strip()
        profile_photo = self.request.get('prof_photo')
        website = self.request.get('website').strip()        
        if user and name and roll and stream:
            u = Users(email = user.email(), name=name, roll_number=int(roll), stream=stream)
            if website:
                url_o   = urlparse(website)
                website = "http://" + url_o[1] + url_o[2]
                if checkUrl(website):
                    u.website = website

            if profile_photo:
                p               = db.Blob(str(profile_photo))
                u.profile_photo = p


            if skills:
                u.skills           = [s.strip() for s in skills.split(",")]

            if skills_to_learn:
                u.skills_to_learn = [s.strip() for s in skills_to_learn.split(",")]

            u.put()

            self.redirect("/")
        else:
            self.redirect("/register")

class AddTopic(Handler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_obj = get_user(user.email())

            if user_obj:
                self.render('add_topic-new.html', user=user_obj, logout_link=users.create_logout_url('/'), categories=CATEGORIES)
            else:
                self.redirect("/register")
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        user = users.get_current_user()
        if user:
            title = self.request.get('title').strip()
            category = self.request.get('category').strip()
            description_student = self.request.get("description_student").strip()
            user_obj = get_user(user.email())
            if user_obj and title and description_student and category:
                u = Topics(created_by = user_obj, title=title, list_of_students=[str(user_obj.key())], description_student=description_student, category=category)
                u.put()
                self.redirect("/home")
            else:
                self.redirect("/")
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Image(webapp2.RequestHandler):
    def get(self):
        my = db.get(self.request.get('img_id'))
        if my.profile_photo:
            ty = my.profile_photo.split(".")[-1]
            if ty == 'jpg':
                ty = 'jpeg'
            self.response.headers['Content-Type'] = 'image/' + ty
            self.response.out.write(my.profile_photo)
        else:
            self.error(404)

class UserProfile(Handler):
    def get(self, id):
        user = db.get(id)
        u = users.get_current_user()
        if u:
            self.render('profile.html', user=user, logout_link=users.create_logout_url('/'))
        else:
            self.render("index.html", profile=user, streams=STREAMS)

class AllUClasses(Handler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_obj = get_user(user.email())
            if user_obj:
                u = db.GqlQuery("SELECT * FROM Topics WHERE when != :1 AND when >= :2 ORDER BY when", None, datetime.today())
                classes = u.fetch(None)
                
                for r in classes:
                    for student in range(0, len(r.list_of_students)):
                        s = r.list_of_students[student]
                        r.list_of_students[student] = db.get(s)
                    for teacher in range(0, len(r.list_of_teachers)):
                        s = r.list_of_teachers[teacher]
                        r.list_of_teachers[teacher] = db.get(s)
                
                self.render("upcoming.html", classes=classes, user=user_obj, logout_link=users.create_logout_url('/'))
            else:
                self.redirect('/register')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class TopicProfile(Handler):
    def get(self, id):
        topic = db.get(id)
        u = users.get_current_user()

        if u:
            user_obj = get_user(u.email())
            if user_obj:
                for student in range(0, len(topic.list_of_students)):
                    s = topic.list_of_students[student]
                    topic.list_of_students[student] = db.get(s)
                for teacher in range(0, len(topic.list_of_teachers)):
                    s = topic.list_of_teachers[teacher]
                    topic.list_of_teachers[teacher] = db.get(s)
                self.render("class.html", topic=topic, user=user_obj, logout_link=users.create_logout_url('/'))
            else:
                self.redirect('/register')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class UserHome(Handler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        else:
            user_obj = get_user(user.email())

            u = db.GqlQuery("SELECT * FROM Topics WHERE when != :1 ORDER BY when", None)
            u = u.fetch(None)

            upcoming_courses_user_is_teacher_of = []
            upcoming_courses_user_is_student_of = []

            for r in u:
                if str(user_obj.key()) in r.list_of_teachers:
                    for teacher in range(0, len(r.list_of_teachers)):
                        s = r.list_of_teachers[teacher]
                        r.list_of_teachers[teacher] = db.get(s)
                    upcoming_courses_user_is_teacher_of.append(r)

            r = 0
            for r in u:
                if str(user_obj.key()) in r.list_of_students:
                    for student in range(0, len(r.list_of_students)):
                        s = r.list_of_students[student]
                        r.list_of_students[student] = db.get(s)
                    upcoming_courses_user_is_student_of.append(r)

            self.render('home.html', user=user_obj, logout_link=users.create_logout_url('/'), upcoming_courses_user_is_student_of=upcoming_courses_user_is_student_of, upcoming_courses_user_is_teacher_of=upcoming_courses_user_is_teacher_of)

class SignIn(Handler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_obj = get_user(user.email())
            if user_obj:
                self.redirect("/home")
            else:
                self.redirect("/register")
        else:
            self.redirect("/register")

class RequestedClasses(Handler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_obj = get_user(user.email())
            if user_obj:
                u = db.GqlQuery("SELECT * FROM Topics WHERE when = :1 ORDER BY created", None)
                classes = u.fetch(None)
                
                for r in classes:
                    for student in range(0, len(r.list_of_students)):
                        s = r.list_of_students[student]
                        r.list_of_students[student] = db.get(s)
                    for teacher in range(0, len(r.list_of_teachers)):
                        s = r.list_of_teachers[teacher]
                        r.list_of_teachers[teacher] = db.get(s)
    
                self.render("requested_classes.html", classes=classes, user=user_obj, logout_link=users.create_logout_url('/'))
            else:
                self.redirect('/register')
        else:
            self.redirect(users.create_login_url(self.request.uri))        

class AddMentor(Handler):
    def get(self, id):
        user = users.get_current_user()
        user_obj = get_user(user.email())

        if user_obj:
            topic = db.get(id)
            if len(topic.list_of_teachers) >= 1:
                if user_obj.key() not in topic.list_of_teachers:
                    topic.list_of_teachers.append(str(user_obj.key()))
                    topic.put()
                    self.redirect("/upcoming_classes")
                else:
                    self.redirect("/")
            else:
                self.render('mentor_that.html', topic=topic, user=user_obj, logout_link=users.create_logout_url('/'))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self, id):
        topic = db.get(id)
        user = users.get_current_user()
        user_obj = get_user(user.email())
        teacher_description = self.request.get('teacher_description').strip()
        date = self.request.get('date').strip()
        time = self.request.get('time').strip()
        location = self.request.get('location').strip()

        if user_obj and teacher_description and date and time and location:
            topic.user = user_obj
            topic.description_teacher = teacher_description
            topic.when = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
            topic.location = location
            topic.list_of_teachers = [str(user_obj.key())]
            topic.put()
            self.redirect("/class/" +str(topic.key()))
        else:
            self.redirect("/")  

class AddStudent(Handler):
    def get(self, id):
        user = users.get_current_user()
        user_obj = get_user(user.email())

        if user_obj:
            topic = db.get(id)
            if len(topic.list_of_students) >= 1:
                if user_obj.key() not in topic.list_of_teachers:
                    topic.list_of_students.append(str(user_obj.key()))
                    topic.put()
                    self.redirect("/upcoming_classes")
                else:
                    self.redirect("/")
        else:
            self.redirect(users.create_login_url(self.request.uri))


    def post(self, id):
        topic = db.get(id)
        user = users.get_current_user()
        user_obj = get_user(user.email())
        teacher_description = self.request.get('teacher_description').strip()
        date = self.request.get('date').strip()
        time = self.request.get('time').strip()
        location = self.request.get('location').strip()

        if user_obj and teacher_description and date and time and location:
            topic.user = user_obj
            topic.description_teacher = teacher_description
            topic.when = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
            topic.location = location
            topic.list_of_teachers = [str(user_obj.key())]
            topic.put()
            self.redirect("/class/" +str(topic.key()))
        else:
            # do something useful here!
            self.redirect("/")


app = webapp2.WSGIApplication([
    ('/', Home),
    ('/register', Register),
    ('/user/(.+)', UserProfile),
    ('/add_class', AddTopic),
    ('/mentor_that/(.+)', AddMentor),
    ('/class/(.+)', TopicProfile),
    ('/img', Image),
    ('/home', UserHome),
    ('/sign_in', SignIn),
    ('/upcoming_classes', AllUClasses),
    ('/class/(.+)', TopicProfile),
    ('/requested_classes', RequestedClasses),
    ('/attend_that/(.+)', AddStudent)
], debug=True)