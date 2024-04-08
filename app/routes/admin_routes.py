import sqlite3

from flask import Blueprint, render_template, request, redirect

from app.services.books import get_books_by_section, get_all_user_issued_books, add_book, get_sections, add_section, \
    get_section_by_id, update_section, delete_section, delete_book, update_book, revoke_book, \
    get_all_current_user_books, get_all_requested_books

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admins/<string:admin_id>/adminDashboard', methods=['GET'])
def admin_dashboard(admin_id):
    return render_template('admin_dashboard.html',admin_id=admin_id)

@admin_bp.route('/admins/<string:admin_id>/sections/<string:section_id>/books', methods=['GET'])
def get_user_assigned_books(admin_id,section_id):
    is_add_book = request.args.get('add_books')
    books_list = get_all_user_issued_books(section_id)
    section_name = get_section_by_id(str(section_id))['title']
    edit_book_id = request.args.get('edit_book_id')
    if is_add_book:
        return render_template('admin_section_books.html',admin_id=admin_id,section_id=section_id,books=books_list,add_new_book=True,section_name=section_name)
    if edit_book_id:
        return render_template('admin_section_books.html',admin_id=admin_id,section_id=section_id,books=books_list,add_new_book=False,section_name=section_name,edit_book_id=int(edit_book_id))
    return render_template('admin_section_books.html',admin_id=admin_id,section_id=section_id,books=books_list,add_new_book=False,section_name=section_name)

@admin_bp.route('/admins/<string:admin_id>/sections/<string:section_id>/books', methods=['POST'])
def add_new_book(admin_id,section_id):
    title = request.form['title']
    author = request.form['author']
    added = add_book(title,author,section_id)
    if added:
        return get_user_assigned_books(admin_id,section_id)
    else:
        return render_template('admin_section_books.html',admin_id=admin_id,section_id=section_id,error='Book already exists')

@admin_bp.route('/admins/<string:admin_id>/sections/', methods=['GET'])
def list_sections(admin_id,justAdded=False):
    section_list=get_sections()
    edit_section_id = request.args.get('edit_section_id')
    print(edit_section_id)
    if request.args.get('add_section') and not justAdded:
        return render_template('admin_sections.html',admin_id=admin_id,sections=section_list,add_section=True)
    if edit_section_id:
        return render_template('admin_sections.html',admin_id=admin_id,sections=section_list,add_section=False,edit_section_id=int(edit_section_id))
    return render_template('admin_sections.html',admin_id=admin_id,sections=section_list,add_section=False)
@admin_bp.route('/admins/<string:admin_id>/sections/', methods=['POST'])
def add_new_section(admin_id):
    title = request.form['title']
    description = request.form['description']
    date= request.form['date']
    added = add_section(title,description,date)
    if added:
        return list_sections(admin_id,justAdded=True)
    else:
        return render_template('admin_sections.html',admin_id=admin_id,error='Section already exists')
@admin_bp.route("/admins/<string:admin_id>/sections/updateSection/<string:section_id>",methods=['POST'])
def update_section_post(admin_id,section_id):
    title = request.form['title']
    description = request.form['description']
    date= request.form['date']
    success=update_section(section_id,title,description,date)
    if success:
        return redirect(f"/admins/{admin_id}/sections")
    else:
        return render_template('admin_sections.html',admin_id=admin_id,error='Section Update Issue')


@admin_bp.route("/admins/<string:admin_id>/sections/deleteSection/<string:section_id>",methods=['GET'])
def delete_section_get(admin_id,section_id):
    success=delete_section(section_id)
    if success:
        return redirect(f"/admins/{admin_id}/sections")
    else:
        return render_template('admin_sections.html',admin_id=admin_id,error='Section Delete Issue')
@admin_bp.route('/admins/<string:admin_id>/sections/<string:section_id>/books/<string:book_id>/deleteBook', methods=['GET'])
def delete_book_get(admin_id,section_id,book_id):
    success=delete_book(book_id)
    if success:
        return redirect(f"/admins/{admin_id}/sections/{section_id}/books")
    else:
        return render_template('admin_section_books.html',admin_id=admin_id,section_id=section_id,error='Book Delete Issue')
@admin_bp.route('/admins/<string:admin_id>/sections/<string:section_id>/books/<string:book_id>/updateBook', methods=['POST'])
def update_book_post(admin_id,section_id,book_id):
    title = request.form['title']
    author = request.form['author']
    success=update_book(book_id,title,author)
    if success:
        return redirect(f"/admins/{admin_id}/sections/{section_id}/books")
    else:
        return render_template('admin_section_books.html',admin_id=admin_id,section_id=section_id,error='Book Update Issue')

@admin_bp.route('/admins/<string:admin_id>/revokeBook/<string:user_requested_books_id>', methods=['GET'])
@admin_bp.route('/admins/<string:admin_id>/sections/<string:section_id>/books/<string:book_id>/revokeBook/<string:user_requested_books_id>', methods=['GET'])
def revoke_book_get(admin_id,user_requested_books_id,section_id=None,book_id=None):
    success=revoke_book(user_requested_books_id)

    if not success:
        return render_template('admin_dashboard.html',admin_id=admin_id,error='Book Revoke Issue')
    if section_id and book_id:
        return redirect(f"/admins/{admin_id}/sections/{section_id}/books")
    return redirect(f"/admins/{admin_id}/adminDashboard")

@admin_bp.route('/admins/<string:admin_id>/requests/', methods=['GET'])
def get_requests_view(admin_id):
    book_list = get_all_current_user_books()
    request_list=get_all_requested_books()

    return render_template('admin_requests.html',admin_id=admin_id,books=book_list,requests=request_list)
