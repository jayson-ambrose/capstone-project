from flask import request, make_response, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Review, Backlog, Book

app.secret_key = 'change this secret key'

class Logout(Resource):
    def get(self):
        session['user_id'] = None
        return {}, 204
    
    def delete(self):
        print(session['user_id'])
        session['user_id'] = None
        return {}, 204

class Login(Resource):

    def post(self):
        req_data = request.get_json()
        user = User.query.filter(User.username == req_data['username']).first()       
        
        try:
            if user.auth(req_data['password']) == False:
                print ('wrong password')
                return make_response({"error":"wrong password enterred"}, 401) 
                      
            session['user_id'] = user.id

            return make_response(user.to_dict(), 200)
        
        except:
            return make_response( {'error': '401 user not found or incorrect password'}, 401)

class Users(Resource):
    def get(self):
        user_list = []
        for user in User.query.all():
            user_list.append(user.to_dict())

        return make_response(user_list, 200)
    
    def post(self):
        req = request.get_json()

        if req['password'] != req['re_password']:
            return make_response({'error':'401: passwords do not match.'}, 401)
        
        user = User(username=req.get('username'), password=req.get('password'))
        try:
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            print(session['user_id'])
            return make_response(user.to_dict(rules=("reviews.book",)), 201)
        
        except IntegrityError:
            db.session.rollback()
            return make_response({'error': 'error 400: Username already taken.'}, 400) 

class UsersById(Resource):
    
    def get(self, id):
        user = User.query.filter(User.id == id).one_or_none()
        if user:
            return make_response(user.to_dict())
        return make_response({"error": "error 404: user not found"}, 404) 

    def delete(self, id):
        user = User.query.filter(User.id == id).one_or_none()

        try:
            db.session.delete(user)
            db.session.commit()
            session['user_id'] = None
            return({"message":"account deleted"}, 204)
        
        except:
            return make_response({}, 404)
        
    def patch (self, id):
        user = User.query.filter(User.id == id).one_or_none()
        if not user:
            return make_response({"error":"error 404: user not found, unable to change password."}, 404)
        
        req = request.get_json()

        if req['type'] == 'change_pw':

            if user.auth(req['old_password']) == False:
                    print ('wrong password')
                    return make_response({"error":"old password incorrect."}, 401)
            else:
                print('old password is correct <--------')         
            
            if req['password'] == req['old_password']:
                return make_response({"error":"error 401: new password and old password must not match."})
            else:
                print('old and new passwords do not match <--------')        

            if req['password'] != req['re_password']:
                return make_response({'error':'401: passwords do not match.'}, 401)
            else:
                print('new password and re-new password match <--------')
                    
            try:
                user.password = req['password']
                db.session.add(user)
                db.session.commit()
                return make_response({'message': 'password successfully changed.'}, 200)

            except:
                return make_response({"error":"something went horribly wrong."}, 402) 
            
        if req['type'] == 'change_fav_author':

            try:
                user.favorite_author = req['author']
                db.session.add(user)
                db.session.commit()
                return make_response(user.to_dict(), 200)
            
            except:
                return make_response({'error': '401: failed to change favorite author'})
            
        if req['type'] == 'change_fav_title':

            try:
                user.favorite_title = req['title']
                db.session.add(user)
                db.session.commit()
                return make_response(user.to_dict(), 200)
            
            except:
                return make_response({'error': '401: failed to change favorite author'})

class Books(Resource):

    def get(self):
        bookList = []
        for book in Book.query.all():
            bookList.append(book.to_dict(rules={'-users', '-reviews', '-backlogs'}))

        return make_response(bookList, 200)
    
    def post(self):
        req = request.get_json()
        book = Book.query.filter(Book.isbn == req['isbn']).one_or_none()
        
        if not book:
            new_book = Book(title=req['title'], author=req['author'], isbn=req['isbn'])
            try:
                db.session.add(new_book)
                db.session.commit()                              
                return make_response(new_book.to_dict(only=('title', 'id', 'isbn', 'author')), 201)
            
            except:
                return make_response({'error': '400: Invalid information, unable to add book.'}, 400)

        else:
            print('Book found in database. Returned book values')
            return make_response(book.to_dict(only=('title', 'id', 'isbn', 'author')), 200)

class BooksById(Resource):
    def get(self, id):
        book = Book.query.filter(Book.id == id).one_or_none()
        return make_response(book.to_dict(only=('title', 'id', 'isbn', 'author')), 200)

class Reviews(Resource):
    def get(self):
        reviews_list = []
        for review in Review.query.all():
            reviews_list.append(review.to_dict(only=('review_text', 'rating', 'id', 
                                                     'user', '-user.reviews', '-user.backlogs')))

class ReviewsByBookId(Resource):
    def get(self, id):
        book = Book.query.filter(Book.id == id).one_or_none()
        reviews_list = []
        for review in book.reviews:
            reviews_list.append(review.to_dict(only=('review_text', 'rating', 'id', 
                                                     'user', '-user.reviews', '-user.backlogs')))
        if len(reviews_list) <= 0:
            return make_response({"error":"error 404: No reviews found for this book"}, 404)
        return make_response(reviews_list, 200)
    
    def post(self, id):

        req = request.get_json()

        print(req)

        rev_user = User.query.filter(User.id == req['user_id']).one_or_none()
        rev_book = Book.query.filter(Book.id == id).one_or_none() 

        try:
            new_review = Review(rating=req['rating'], review_text=req['text'], user=rev_user, book=rev_book)

            db.session.add(new_review)
            print('before submit')
            db.session.commit()
            print('after submit')

            return(new_review.to_dict(only=('review_text', 'rating', 'id', 
                                            'user', '-user.reviews', '-user.backlogs')), 201)            

        except:
            return make_response({'error': '400: somethings not right'}, 400)    

class Backlogs(Resource):

    def get(self):

        backlogList = []
        for backlog in Backlog.query.all():
            backlogList.append(backlog.to_dict())

        return make_response(backlogList, 200)
        
    
    def post(self):

        req_data = request.get_json()
        print(req_data)

        print(session.get('user_id'))

        backlog_user = User.query.filter(User.id == session.get('user_id')).one_or_none()
        book = Book.query.filter(Book.id == req_data['id']).one_or_none() 

        backlog = Backlog(completed=0, user=backlog_user, book=book)

        if backlog.book in backlog_user.books_backlogged:
            return make_response({"error": "book already backlogged"}, 400)

        try:            
            db.session.add(backlog)
            db.session.commit()            

            return make_response(backlog.to_dict(), 201)

        except:
            return make_response({"error": "something went wrong"}, 400)
        
class CheckSession(Resource):    

    def get(self):
        print (session.get('user_id'))
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict()
        else:
            return {'message': '401: Not Authorized'}, 401
        

api.add_resource(Login,'/login')
api.add_resource(Users, '/users')
api.add_resource(Backlogs, '/backlogs')
api.add_resource(Logout, '/logout')
api.add_resource(Books, '/books')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ReviewsByBookId, '/books/<int:id>/reviews')
api.add_resource(UsersById, '/users/<int:id>')

if __name__ == '__main__':
    app.run(port=5055, debug=True)