import os
from os import remove
import codecs
from shutil import move, rmtree, copytree, copyfile
import re

# the directory in the jekyll folder where you'll be dumping things.
JEKYLL_DIR = 'book/'
GITBOOK_DIR = '/Users/brandon/GitBook/Library/Import/introduction-to-text-analysis'


def clean_jekyll_dir():
    if os.path.exists(JEKYLL_DIR):
        rmtree(JEKYLL_DIR)


def clean_new_dir(destination_dir=JEKYLL_DIR):
    # move assets to asset folder
    rmtree('assets')
    rmtree('book/.git')
    move('book/assets', 'assets')
    # delete extra files from gitbook
    to_delete = ['book/.gitignore', 'book/book.json', 'book/cover.jpg',
                 'book/contexts-and-claims.md', 'book/GLOSSARY.md',
                 'book/schedule.md']
    for fn in to_delete:
        remove(fn)
    # move summary to includes folder
    if os.path.exists('_includes/SUMMARY.md'):
        remove('_includes/SUMMARY.md')
    move('book/SUMMARY.md', '_includes')
    # move README to includes folder
    if os.path.exists('_includes/README.md'):
        remove('_includes/README.md')
    copyfile('book/README.md', '_includes/README.md')


def export_from_gitbook(source_dir=GITBOOK_DIR, destination_dir=JEKYLL_DIR):
    clean_jekyll_dir()
    copytree(source_dir, destination_dir)
    clean_new_dir(destination_dir)


def manifest(target_dir):
    """given a corpus directory return the files in it"""
    texts = []
    for (root, _, files) in os.walk(target_dir):
        for fn in files:
            if fn[0] == '.':
                pass
            else:
                path = os.path.join(root, fn)
                texts.append(path)
    return texts


def add_header(fn, fin, fout):
    toc = {'Preface': 0, 'Acknowledgements': 1,
           'Introduction': 2, 'Issues in Digital Text Analysis': 3,
           'Close Reading': 4, 'Crowdsourcing': 5,
           'Digital Archives': 6, 'Data Cleaning': 7,
           'Cyborg Readers': 8, 'Reading at Scale': 9,
           'Topic Modeling': 10, 'Classifiers': 11,
           'Sentiment Analysis': 12, 'Conclusion': 13}
    line = fin.readline().strip()
    path = os.path.split(fn)
    if line != '---' and path[0] == 'book':
        title = re.sub(r'#+\s+', '', line)

        page_id = toc[title]
        yaml_header = """---
layout: page
title: {title}
id: {page_id}
---""".format(**locals())
        fout.write(yaml_header)
    elif line != '---' and path[0] != 'book':
        title = re.sub(r'#+', '', line)
        yaml_header = """---
layout: lesson
title: {title}
---""".format(**locals())
        fout.write(yaml_header)
    else:
        fout.write('---\n')


def convert_file(fn, header=True):
    with codecs.open(fn, 'r+', 'utf8') as fin:
        with codecs.open(fn + '_temp', 'w', 'utf8') as fout:
            if header:
                add_header(fn, fin, fout)
            for line in fin.readlines():
                line = convert_link(line)
                fout.write(line)
        remove(fn)
        move(fn + '_temp', fn)


def convert_link(line):
    line = re.sub(r'\]\((?!\/|http)', '](/', line)
    line = re.sub(r'\]\((?!\/textanalysis|\/assets|http)',
                  '](/textanalysiscoursebook/book', line)
    line = re.sub(r'\]\(/assets', '](/textanalysiscoursebook/assets', line)
    line = re.sub(r'\.md', '', line)
    line = re.sub(r'\.md\)$', ')', line)
    line = re.sub(r'src=\"/assets/','src=\"/textanalysiscoursebook/assets/',line)
    return line


def main():
    export_from_gitbook()
    for fn in manifest(JEKYLL_DIR):
        print(fn)
        convert_file(fn)
    convert_file('_includes/SUMMARY.md', False)
    convert_file('_includes/README.md', False)
    convert_file('book/README.md')


if __name__ == '__main__':
    main()
