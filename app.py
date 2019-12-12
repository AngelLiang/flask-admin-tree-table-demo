from sqlalchemy_mptt.mixins import BaseNestedSets

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_sqlalchemy import SQLAlchemy


####################################################################
# extensions

db = SQLAlchemy()
# 因为依赖 bootstrap3， 所以一定要设置 template_mode='bootstrap3'
admin = Admin(template_mode='bootstrap3')


app = Flask(__name__)
db.init_app(app)
db.app = app
admin.init_app(app)

app.config['SECRET_KEY'] = '123456790'
# Create in-memory database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'data.sqlite'


####################################################################
# model

class Tree(db.Model, BaseNestedSets):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __str__(self):
        return '{}'.format(self.name)


def tree2schema(tree):
    return {
        'id': tree.id,
        'name': tree.name,
        'left': tree.left,
        'right': tree.right,
        'parent_id': tree.parent_id,
        'tree_id': tree.tree_id,
    }

####################################################################
# admin view


class TreeTableConfigMixin(object):
    """树形表格专用配置混入类"""
    # 设置 list_template
    list_template = 'admin/model/tree_table.html'

    # 禁止分页，直接获取该数据表所有数据
    page_size = None

    # 禁止设置每页显示的数量
    can_set_page_size = False

    # 禁止任何字段的排序，以免干扰 treegrid.js 显示正确的数据顺序
    column_sortable_list = []

    # 默认以 left 字段排序，使 treegrid.js 能正确显示树形表格
    column_default_sort = 'left'


class TreeView(TreeTableConfigMixin, ModelView):
    """
    注意 TreeTableConfigMixin 要放在 ModelView 前面
    """
    column_display_pk = True
    column_list = ['id', 'name', 'left',
                   'right', 'parent_id', 'level', 'tree_id']

    can_view_details = True
    can_edit = False
    can_delete = True


admin.add_view(TreeView(Tree, db.session))

####################################################################
# initdata


def initdata(count=10):
    db.drop_all()
    db.create_all()

    trunk = Tree(name="Trunk")
    db.session.add(trunk)
    for i in range(count):
        branch = Tree()
        branch.name = "Branch " + str(i+1)
        branch.parent = trunk
        db.session.add(branch)
        for j in range(5):
            leaf = Tree()
            leaf.name = "Leaf " + str(j+1)
            leaf.parent = branch
            db.session.add(leaf)
            for k in range(3):
                item = Tree()
                item.name = "Item " + str(k+1)
                item.parent = leaf
                db.session.add(item)
    db.session.commit()


if __name__ == "__main__":
    initdata()
    app.run(debug=True)
