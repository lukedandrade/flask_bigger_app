from datetime import datetime
from app import lm
from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db
from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, RegisterForm, EditForm, Edit_for_adminForm, PostForm, EditPostForm
from .models import User, Permission, Post
from .decorators import admin_required, permission_required

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('custom_error.html', error_code=404), 404

@app.errorhandler(403)
def no_permissions(e):
    return render_template('custom_error.html', error_code=403), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('custom_error.html', error_code=500), 500

@app.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For admin"

@app.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For moderators"


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    user = g.user
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object(),
                    timestamp=datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        flash('Post registrado')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, error_out=True)
    posts = pagination.items
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts,
                           form=form,
                           pagination=pagination,
                           permission=Permission)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('Login teve sucesso')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',
                           title='Sign In',
                           form=form)


def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember= remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    if user == None:
        flash('User %s not found.' % (nickname))
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session['nickname'] = form.nickname.data
        session['email'] = form.email.data
        session['password'] = form.password.data
        session['confirm password'] = form.c_password.data
        session['img_link'] = form.img_link.data
        if session['password'] == session['confirm password']:
            new_user = User(nickname=session['nickname'], email=session['email'], password=session['password'],
                            profile_img=session['img_link'])
            db.session.add(new_user)
            db.session.commit()
            flash('Usuário %s criado' % (session['nickname']))
            return redirect(url_for('login'))
        else:
            flash('Erro')
            return redirect(url_for('register'))
    return render_template('register.html',
                           title='Sign In',
                           form=form)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

@app.route('/edit_for_admin/<nickname>', methods=['GET', 'POST'])
@admin_required
@login_required
def edit_for_admin(nickname):
    form = Edit_for_adminForm()
    user_being_edited = User.query.filter_by(nickname=nickname).first_or_404()
    if form.validate_on_submit():
        user_being_edited.nickname = form.nickname.data
        user_being_edited.about_me = form.about_me.data
        user_being_edited.email = form.email.data
        user_being_edited.role_id = form.role_id.data
        user_being_edited.profile_img = form.img_link.data
        db.session.add(user_being_edited)
        db.session.commit()
        user_being_edited = User.query.filter_by(nickname=user_being_edited.nickname).first_or_404()
        flash('Your changes have been saved, mr. Admin.')
        return redirect(url_for('user', nickname=user_being_edited.nickname))
    return render_template('edit_for_admin.html',
                           form=form,
                           user=user_being_edited)

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('posts.html', post=post)

@app.route('/edit_post/<int:id>', methods=['POST', 'GET'])
@permission_required(Permission.MODERATE_COMMENTS)
def edit_post(id):
    post_being_edited = Post.query.get_or_404(id)
    form = EditPostForm()
    if form.validate_on_submit():
        post_being_edited.body = form.new_body.data
        db.session.add(post_being_edited)
        db.session.commit()
        flash('Your changes have been saved, mr. Moderator')
        return redirect(url_for('index'))
    return render_template('edit_posts.html',
                           post=post_being_edited,
                           form=form)