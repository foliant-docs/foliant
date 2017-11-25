# Hello

<if flags="foo, bar" kind="all">
Foo and Bar.
</if>

<if flags="baz" kind="none">
Not baz.
</if>

## Usage

<if flags="foo">
  <include sethead="2" nohead="true">
    $foliant$^README.md#Foliant
  </include>
</if>

<seqdiag caption="This is a caption">
seqdiag {
  browser  -> webserver [label = "GET /index.html"];
  browser <-- webserver;
  browser  -> webserver [label = "POST /blog/comment"];
              webserver  -> database [label = "INSERT comment"];
              webserver <-- database;
  browser <-- webserver;
}
</seqdiag>
