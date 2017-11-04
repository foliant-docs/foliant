# Hello

````if any foo
Foo.
''''

````if all foo bar
Foo.

Bar.
''''

````include ../../README.md''''

````include <foliant>README.md#Foliant''''

````seqdiag This is a caption
seqdiag {
  browser  -> webserver [label = "GET /index.html"];
  browser <-- webserver;
  browser  -> webserver [label = "POST /blog/comment"];
              webserver  -> database [label = "INSERT comment"];
              webserver <-- database;
  browser <-- webserver;
}
''''
