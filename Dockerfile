FROM ruby:2.5

EXPOSE 4000
WORKDIR /usr/src/app

COPY Gemfile Gemfile ./
RUN gem install bundle
RUN bundle install
RUN bundle exec jekyll serve