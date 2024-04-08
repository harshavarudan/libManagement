
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.books import get_my_books_current, get_my_books_completed, get_book_by_id, add_user_request_entry, \
    no_of_requested_books_user, get_books_read_per_section, get_section_distribution, return_book,get_books
import matplotlib.pyplot as plt
import io
import base64

user_bp = Blueprint('user', __name__)


@user_bp.route('/users/<string:user_id>/userDashboard', methods=['GET'])
def user_dashboard(user_id):
    return render_template('user_dashboard.html',user_id=user_id)
#/users/userID/userDashboard

@user_bp.route('/users/<string:user_id>/userDashboard/books', methods=['GET'])
def user_dashboard_books(user_id):
    search_term = request.args.get('search_term')
    filter_by = request.args.get('filter_by')

    # Get filtered books based on search term and filter criterion
    books_list = get_books(user_id,search_term, filter_by)

    return render_template('user_dashboard_books.html', user_id=user_id, books=books_list)


@user_bp.route('/users/<string:user_id>/userDashboard/myBooks',methods=['GET'])
def user_dashboard_my_books(user_id):
    my_completed_books_list = get_my_books_completed(user_id)
    my_current_books_list = get_my_books_current(user_id)
    return render_template('user_dashboard_my_books.html',user_id=user_id,my_completed_books=my_completed_books_list,my_current_books=my_current_books_list)

@user_bp.route('/users/<string:user_id>/userDashboard/books/request',methods=['POST'])
def user_dashboard_books_request(user_id):
    book_id = request.form['book_id']
    days_requested = request.form['days_requested']
    try:
        days_requested_int = int(days_requested)
    except ValueError:
        flash('Please enter a valid number of days.', 'error')
        return redirect(url_for('user.user_dashboard_books', user_id=user_id))

    book = get_book_by_id(book_id)
    no_of_books_requested = no_of_requested_books_user(user_id)

    if no_of_books_requested >= 5:
        flash('You can request upto 5 books only.','error')
        user_id = request.view_args['user_id']
        user_dashboard_books_redirect = "/users/" + str(user_id) + "/userDashboard" + "/books"
        return redirect(user_dashboard_books_redirect)
    if book:
        add_user_request_entry(user_id,book_id,days_requested_int)
        flash('Requested!','success')
    else:
        flash('Book not found!','error')
    user_id = request.view_args['user_id']
    user_dashboard_books_redirect = "/users/" + str(user_id) + "/userDashboard" + "/books"
    return redirect(user_dashboard_books_redirect)

@user_bp.route('/users/<string:user_id>/userDashboard/stats', methods=['GET'])
def user_stats(user_id):
    # Get data for the current user
    books_read_per_section = get_books_read_per_section(user_id)
    section_names = [section['section_title'] for section in books_read_per_section]
    books_read_counts = [section['books_read'] for section in books_read_per_section]

    # Generate bar chart
    plt.figure(figsize=(10, 5))
    plt.bar(section_names, books_read_counts)
    plt.xlabel('Book Section')
    plt.ylabel('Number of Books Read')
    plt.title('Books Read per Section')
    plt.xticks(rotation=45)
    bar_chart_img = io.BytesIO()
    plt.savefig(bar_chart_img, format='png')
    bar_chart_img.seek(0)
    bar_chart_url = base64.b64encode(bar_chart_img.getvalue()).decode()

    # Get section distribution data
    section_distribution = get_section_distribution()
    section_names = [section['title'] for section in section_distribution]
    book_counts = [section['count'] for section in section_distribution]

    # Generate pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(book_counts, labels=section_names, autopct='%1.1f%%')
    plt.title('Section Distribution of All Books')
    pie_chart_img = io.BytesIO()
    plt.savefig(pie_chart_img, format='png')
    pie_chart_img.seek(0)
    pie_chart_url = base64.b64encode(pie_chart_img.getvalue()).decode()

    return render_template('user_stats.html', user_id=user_id, bar_chart_url=bar_chart_url, pie_chart_url=pie_chart_url)

@user_bp.route('/users/<string:user_id>/userDashboard/myBooks/return', methods=['POST'])
def return_book_route(user_id):
    if request.method == 'POST':
        book_id = request.form['book_id']
        if return_book(user_id, book_id):
            flash('Book returned successfully!', 'success')
        else:
            flash('Failed to return book.', 'error')
    return redirect(url_for('user.user_dashboard_my_books', user_id=user_id))



