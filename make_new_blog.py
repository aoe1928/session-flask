import os
import datetime
import shutil
import re
import sys
import argparse


PATH = os.path.dirname(__file__)
# YYYYMM
YYYYMM = datetime.date.today().strftime('%Y%m')
YYYYMMDD = datetime.date.today().strftime('%Y%m%d')
BLOG_PATH = PATH + '/static/src/components/Blogs/'
TEMPLATE_PATH = BLOG_PATH + 'Template.js'
BLOG_INDEX_PATH = PATH + '/static/src/components/Blogs/blogIndex.js'
ROUTE_JS_PATH = PATH + '/static/src/routes.js'


def make_new_js():

    # Check if there is directory
    if not os.path.isdir(BLOG_PATH + YYYYMM):
        os.mkdir(BLOG_PATH + YYYYMM)

    # Copy Template.js as new name

    shutil.copyfile(TEMPLATE_PATH, NEW_BLOG_PATH)

    # rename the className

    with open(NEW_BLOG_PATH, mode='r') as f:
        s = f.read()

    s = s.replace('<h1 className="title">Template</h1>', f'<h1 className="title">{title}</h1>')
    s = s.replace('<div className="Template">', f'<div className="{new_blog}">')


    with open(NEW_BLOG_PATH, mode='w') as f:
        f.write(s)


def route_js():
    ### import modules to route.js #

    with open(ROUTE_JS_PATH, mode='r') as f:
        s = f.read()

    route_js_list = s.split('\n')
    new_route_js_list = route_js_list

    # add import module

    import_line_counter = 9999999
    import_line = f"import {new_blog} from './components/Blogs/{YYYYMM}/{new_blog}.js';"

    for n, line in enumerate(route_js_list):
        if re.match(r'\/\* Blogs end \*\/', line):
            import_line_counter = n

    new_route_js_list.insert(import_line_counter, import_line)

    route_js_list = new_route_js_list
    # add react path

    path_line_counter = 9999999
    path_line = f'        <Route path="{new_blog}" components={"{" + new_blog + "}"} />'

    for n, line in enumerate(route_js_list):
        if line == '        {/* Blog Route End */}':
            path_line_counter = n

    new_route_js_list.insert(path_line_counter, path_line)

    new_route_js = '\n'.join(new_route_js_list)

    # commit to route.js

    with open(ROUTE_JS_PATH, mode='w') as f:
        f.write(new_route_js)


def blog_index():
    with open(BLOG_INDEX_PATH, mode='r') as f:
        s = f.read()

    blog_index_list = s.split('\n')
    new_blog_index_list = blog_index_list

    blog_index_counter = 999999
    blog_index_line = f'    new BlogIndex("{new_blog}", "{title}", "{YYYYMMDD}", "{status}"),'

    for n, line in enumerate(blog_index_list):
        if line == '    // Index End':
            blog_index_counter = n

    new_blog_index_list.insert(blog_index_counter, blog_index_line)

    new_blog_index = '\n'.join(new_blog_index_list)

    with open(BLOG_INDEX_PATH, mode='w') as f:
        f.write(new_blog_index)


def main():

    make_new_js()
    route_js()
    blog_index()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--newblog", help="new blog title")
    parser.add_argument("-t", "--title", help="new blog title")
    parser.add_argument("-s", "--status", help="blog status: usage, p = personal, rn = THE ROMANS NEWS, rw = THE ROMANS WIKI")
    args = parser.parse_args()

    if (len(sys.argv) <= 2):
        print('usage: new_blog="new blog title" title="new blog title" status="blog status"')
    else:
        if args.status not in ["p", "rn", "rw"]:
            print("invalid status")
        else:
            new_blog = args.newblog
            title = args.title
            status = args.status
            NEW_BLOG_PATH = BLOG_PATH + YYYYMM + '/' + new_blog + '.js'
            main()