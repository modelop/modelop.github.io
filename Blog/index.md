---
layout: bloghome
title: "Tech Blog"
---

# Latest Posts

{% for post in site.posts %}

<h2 class="posttitle"><a href="{{ post.url }}">{{ post.title }}</a></h2>
By {{ post.author }} on {{ post.date | date: "%a, %b %d, %Y" }}

{{ post.excerpt }}

<div class="blogfooter">
<p class="readmore"><a href="{{ post.url }}">Read the rest of this post</a></p>
</div>

<p> Tags: {% for tag in post.tags %}
{% if forloop.last != true %}
{{ tag }},
{% else %}
{{ tag }}
{% endif %}
{% endfor %}
</p>

{% if forloop.last != true %}
<hr />
{% endif %}

{% endfor %}
