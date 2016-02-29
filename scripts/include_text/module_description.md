# Local search

*It does not matter if a file has an extension or not, if not – "md" will be added. The included files may also have their own includes inside.*

* by absolute path {{/examples/file1.md}};
* using recursion inside of the working directory {{*file1.md}}.

# Gitlab project search

* by absolute path {{git:/exaples/file1.md}};
* using recursion inside of the gitlab project (reference taken from config) {{git:*file1.md}}.

# Chapter extraction

Chapters can be extracted either from gitlab or a local directory. The logic of processing is the same.

## Variants

*The given examples are made as "local search" using recursion without "md" extension*

* take text from the first chapter up to end {{*file1:First}};
* take text from the first chapter up to the second one {{*file1:First-Second}};
* take text and change the heading levels as needed taking into account the embedded structure {{*file1:First#3}}.