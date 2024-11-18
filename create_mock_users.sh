#!/bin/bash

# Function to create a user
create_user() {
  curl --location 'http://localhost:4200/api/user/register' \
  --header 'Content-Type: application/json' \
  --data-raw "$1"
}

# Create users
create_user '{
  "username": "testusr1",
  "password": "testusr1pass",
  "email": "test1@test.com"
}' &&

create_user '{
  "username": "testusr2",
  "password": "testusr2pass",
  "email": "test2@test.com"
}' &&

create_user '{
  "username": "testusr3",
  "password": "testusr3pass",
  "email": "test3@test.com"
}' &&

create_user '{
  "username": "testusr4",
  "password": "testusr4pass",
  "email": "test4@test.com"
}' &&

create_user '{
  "username": "testusr5",
  "password": "testusr5pass",
  "email": "test5@test.com"
}'
