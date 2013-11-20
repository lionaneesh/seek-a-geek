#!/usr/bin/env python
#
# Copyright 2013 Seek A Geek
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

from google.appengine.ext import db

from Users import Users

class Topics(db.Model):
    created_by    = db.ReferenceProperty(Users)
    title         = db.StringProperty(required = True)
    description_student = db.TextProperty(required = True)
    description_teacher = db.TextProperty()
    list_of_students = db.StringListProperty(required = True)
    list_of_teachers = db.StringListProperty()
    when             = db.DateTimeProperty()
    created       = db.DateTimeProperty(auto_now_add = True)
    category      = db.StringProperty(required = True)
    location      = db.StringProperty()