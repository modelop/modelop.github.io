# Blog posts

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
      <br />
      By {{ post.author }}
      {{ post.excerpt }}
    </li>
  {% endfor %}
</ul>
