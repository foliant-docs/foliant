# Embedding Diagrams

Foliant lets you embed [seqdiag](http://blockdiag.com/en/seqdiag/>) diagrams.

To embed a diagram, put its definition in a fenced code block:

```markdown
    ```seqdiag Optional single-line caption
    seqdiag {
    browser  -> webserver [label = "GET /index.html"];
    browser <-- webserver;
    browser  -> webserver [label = "POST /blog/comment"];
                webserver  -> database [label = "INSERT comment"];
                webserver <-- database;
    browser <-- webserver;
    }
    ```
```

This is transformed into `![Optional single-line caption](diagrams/123-qwe-456-asd.png)`, where `diagrams/123-qwe-456-asd.png` is an image generated from the diagram definition.

# Customizing Diagrams

To use a custom font, create the file `$HOME/.blockdiagrc` and define the full path to the font ([ref](http://blockdiag.com/en/seqdiag/introduction.html#font-configuration)):

```shell
$ cat $HOME/.blockdiagrc
[seqdiag]
fontpath = /usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf
```

You can define [other params](http://blockdiag.com/en/seqdiag/sphinxcontrib.html#configuration-file-options) as well (remove `seqdiag_` from the beginning of the param name).
