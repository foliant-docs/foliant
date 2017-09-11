# Including External Markdown Files

Foliant allows to include Markdown sources from external files. The file can be located on the disk or in a remote git repository.

When you include a file from a git repo, the whole repo is cloned. The repo is cloned only once and is updated during subsequent includes.

Foliant attempts to locate the images referenced in the included documents. First, it checks the path specified in the image directive and 'image' and 'graphics' directories. If the image is not there, it goes one level up and repeats the search. If it reaches root and doesn't find the image, it returns '.'.


## Basic Usage

Here is a local include:

```markdown
{{ ../../external.md }}
```

> **Note**
>
> If you use Foliant in a Docker container, local includes pointing outside the project directory will not be resolved. That's because only the project directory is mounted inside the container.
> 
> To work around that, mount the directories with the localy included files manually.

Here is an include from git:

```markdown
{{ <git@github.com:foliant-docs/foliant.git>path/to/external.md }}
```

Repo URL can be provided in https, ssh, or git protocol.

**Note**

If you use Foliant in a Docker container, use https protocol. Otherwise,
you'll be prompted by git to add the repo host to ``known_hosts``.

If the repo is aliased as "myrepo" in `config.json`_, you can use the alias
instead of the repo URL:

```markdown
{{ <myrepo>path/to/external.md }}
```

You can also specify a particular revision (branch, tag, or commit):

```markdown
{{ <myrepo#mybranch>path/to/external.md }}
```


## Extract Document Part Between Headings

It is possible to include only a part of a document between two headings, a heading and document end, or document beginning and a heading.

Extract part from the heading "From Head" to the next heading of the same level or the end of the document:

```markdown
{{ external.md#From Head }}
```

From "From Head" to "To Head" (disregarding their levels):

```markdown
{{ external.md#From Head:To Head }}
```

From the beginning of the document to "To Head":

```markdown
{{ external.md#:To Head }}
```

All the same notations work with remote includes:

```markdown
{{ <myrepo>external.md#From Head:To Head }}
```


## Heading Options

If you want to include a document but set your own heading, strip the original heading with `nohead` option:

```markdown
{{ external.md#From Head | nohead }}
```

If there is no opening heading, the included content is left unmodified.

You can also set the level for the opening heading for the included source:

```markdown
{{ external.md#From Head | sethead:3 }}
```

The options can be combined:

```markdown
{{ external.md#From Head | nohead, sethead:3 }}
```


## File Lookup

You can include a file knowing only its name, without knowing the full path. Foliant will look for the file recursively starting from the specified directory: for a remote include, it's the repo root directory; for a local one, it's the directory you specify in the path.

Here, Foliant will look for the file in the repo directory:

```markdown
{{ <myrepo>^external.md }}
```

In this case, Foliant will go one level up from the directory with the document containing the include and look for `external.md` recursively:

```markdown
{{ ../^external.md }}
```


## Nested Includes

Included files can contain includes themselves.


## Include Frenzy!

```markdown
{{ <myrepo#mybranch>path/^external.md#From Heading:To Heading | nohead, sethead:3 }}
```
